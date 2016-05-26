#!/usr/bin/env python3
from git import Repo, Git
from operator import methodcaller
import re
import markdown
import argparse
import time, datetime
import requests, json

class Tag:

    template = '(?P<major_version>\\d*)\\.(?P<minor_version>\\d*).(?P<patch_version>\\d*)(?P<suffix>\\.*)?'

    def __init__(self, git_tag):
        self.tag = git_tag
        self.match = re.search(self.template, str(git_tag))
        if self.match:
            self.major_version = self.match.group('major_version')
            self.minor_version = self.match.group('minor_version')
            self.patch_version = self.match.group('patch_version')
            self.suffix = self.match.group('suffix')    
            self.name = self.major_version + "." + self.minor_version + "." + self.patch_version
            if self.suffix:
                self.name += self.suffix

    def calculate_weight(self):
        version = int(self.major_version) * 100000 + int(self.minor_version) * 1000 + int(self.patch_version)
        return version

class Release:
    
    def __init__(self, version):
        self.version = version
        self.issues = set()
        
    def add_feature(self, issue_number):
        self.issues.add(issue_number)

class Herodotus:

    issue_regexp = "([A-Z]+-\\d+)"

    def __init__(self, directory):
        self._repo = Repo(directory)
        self.directory = directory
        assert not self._repo.bare
        
    def get_tags(self):
        tags = []
        for tag in self._repo.tags:
            tags.append(Tag(tag))
        return sorted(tags, key=methodcaller('calculate_weight'))
        
    def get_releases(self, *args, **kwargs):
        sinceTag = kwargs.get('sinceTag', None)
        if sinceTag:
            since = Tag(since)
    
        toTag = kwargs.get('toTag', None)
        if toTag:
            to = Tag(to)
            
        sinceDate  = kwargs.get('sinceDate', None)
        toDate  = kwargs.get('toDate', None)

        tags = self.get_tags()
        releases = []
        for i in range(1, len(tags)):
            released_tag = tags[i]
            if sinceDate and released_tag.tag.commit.committed_date < sinceDate:
                continue
            if toDate and released_tag.tag.commit.committed_date > toDate:  
                continue
            tag_before_release = tags[i-1]
            log = Git(working_dir = self.directory).log(tag_before_release.name + ".." + released_tag.name)
            issues = re.findall(self.issue_regexp, log)
            if issues \
                and (not sinceTag \
                     or (sinceTag.calculate_weight() <= tag_before_release.calculate_weight()) \
                    ) \
                and (not toTag \
                     or (toTag.calculate_weight() >= released_tag.calculate_weight()) \
                    ):
                release = Release(released_tag.name)
                for issue in issues:
                    release.add_feature(issue)
                releases.append(release)
        releases = reversed(releases)
        return releases
        
    def get_unreleased(self):
        tags = self.get_tags()
        last_tag = tags[len(tags) - 1]
        log = Git(working_dir = self.directory).log("HEAD.." + last_tag.name)
        return re.findall(self.issue_regexp, log)

class Marking:
 
    def __init__(self, jira, *args, **kwargs):
        self.url = jira 
        self.filter_url = jira + "/issues/?jql=key%20in%20%28"
        self.issue_url = jira + "/browse/"
        self.name = kwargs.get('name', '')

    def generate(self, releases, format):
        if self.name:
            changelog = "# " + self.name
        else:
            changelog = "# Version History "
        changelog += "\n"
        for release in releases:
            changelog += "\n### Version " + release.version + "\n"
            if release.issues:
                issues_list = list(release.issues)
                overall_filter = self.filter_url + issues_list[0]
                for i in range(1, len(release.issues)):
                    overall_filter = overall_filter + "%2C" + issues_list[i]
                overall_filter = overall_filter + "%29"
                changelog += "\n[View as one Jira filter](" + overall_filter + ")" + "\n\n"
                for issue in release.issues:
                    changelog += "* [" + issue + "]" + "(" + self.issue_url + issue + ")" + "\n"
        if format == 'md':
            return changelog
        if format == 'html':
            return markdown.markdown(changelog)
            
            
def get_cli_args():
    parser = argparse.ArgumentParser(description='Generate changelog')
    parser.add_argument('repo',
                        metavar = 'directory',
                        type = str, 
                        nargs = 1,
                        help = 'git repository')
    parser.add_argument('--jira',
                        dest = 'url',
                        type = str,
                        default = 'http://jira/',
                        help = 'jira endpoint (default - http://jira/)')
    parser.add_argument('--format',
                        dest = 'format',
                        type = str,
                        default = 'md',
                        nargs = "?",
                        help = 'output format ( md or html). Default - md.')
    parser.add_argument('--sinceTag',
                        dest = 'sinceTag',
                        type = str,
                        default = None,
                        nargs = "?")
    parser.add_argument('--toTag',
                        dest = 'toTag',
                        type = str,
                        default = None,
                        nargs = "?")
    parser.add_argument('--sinceDate',
                        dest = 'sinceDate',
                        type = str,
                        default = None,
                        nargs = "?")
    parser.add_argument('--toDate',
                        dest = 'toDate',
                        type = str,
                        default = None,
                        nargs = "?")
    parser.add_argument('--name',
                        dest = 'name',
                        type = str,
                        nargs = "?")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_cli_args()

    pylog = Herodotus(args.repo[0])

    sinceDate = None
    if args.sinceDate:
        sinceDate = time.mktime(datetime.datetime.strptime(args.sinceDate, "%d.%m.%Y").timetuple())

    toDate = None
    if args.toDate:
        toDate = time.mktime(datetime.datetime.strptime(args.toDate, "%d.%m.%Y").timetuple())
    releases = pylog.get_releases(sinceTag = args.sinceTag,
                                     toTag = args.toTag,
                                 sinceDate = sinceDate,
                                    toDate = toDate)

    marking = Marking(jira = args.url,
                      name = args.name)
    print(marking.generate(releases, args.format))
