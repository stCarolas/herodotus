#!/usr/bin/env python3
from git import Repo
from git import Git
from operator import methodcaller
import re
import markdown
import argparse

class Tag:

    # template = '(?P<main_version>\\d*)\\.(?P<major_version>\\d*).(?P<minor_version>\\d*)'
    template = '(?P<main_version>\\d*)\\.(?P<major_version>\\d*).(?P<minor_version>\\d*)\\.?(?P<fix_version>\\d*)?'

    def __init__(self, git_tag):
        self.tag = git_tag
        self.match = re.search(self.template, str(git_tag))
        if self.match:
            self.main_version = self.match.group('main_version')
            self.major_version = self.match.group('major_version')
            self.minor_version = self.match.group('minor_version')
            self.fix_version = self.match.group('fix_version')
            self.name = self.main_version + "." + self.major_version + "." + self.minor_version
            if self.fix_version:
                self.name += "." + self.fix_version

    def calculate_weight(self):
        version = int(self.main_version) * 100000 + int(self.major_version) * 1000 + int(self.minor_version)
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
        since = kwargs.get('since', None)
        if since:
            since = Tag(since)
    
        to = kwargs.get('to', None)
        if to:
            to = Tag(to)

        tags = self.get_tags()
        releases = []
        for i in range(1, len(tags)):
            released_tag = tags[i]
            tag_before_release = tags[i-1]
            log = Git(working_dir = self.directory).log(tag_before_release.name + ".." + released_tag.name)
            issues = re.findall(self.issue_regexp, log)
            if issues \
                and (not since \
                     or (since.calculate_weight() <= tag_before_release.calculate_weight()) \
                    ) \
                and (not to \
                     or (to.calculate_weight() >= released_tag.calculate_weight()) \
                    ):
                release = Release(released_tag.name)
                for issue in issues:
                    release.add_feature(issue)
                releases.append(release)
        releases = reversed(releases)
        return releases
            
     
class Marking:
 
    def __init__(self, jira, *args, **kwargs):
        self.url = jira + "/browse/"
        self.name = kwargs.get('name', '')

    def generate(self, releases, format):
        changelog = "# Version History "
        if self.name:
            changelog += ": " + self.name
        changelog += "\n"
        for release in releases:
            changelog += "\n### Version " + release.version + "\n"
            if release.issues:
                issues_list = list(release.issues)
                overall_filter = "http://jira/issues/?jql=key%20in%20%28" + issues_list[0]
                for i in range(1, len(release.issues)):
                    overall_filter = overall_filter + "%2C" + issues_list[i]
                overall_filter = overall_filter + "%29"
                changelog += "\n[View as one Jira filter](" + overall_filter + ")" + "\n\n"
                for issue in release.issues:
                    changelog += "* [" + issue + "]" + "(" + self.url + issue + ")" + "\n"
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
    parser.add_argument('--since',
                        dest = 'since',
                        type = str,
                        default = None,
                        nargs = "?")
    parser.add_argument('--to',
                        dest = 'to',
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
    releases = pylog.get_releases(since = args.since, to = args.to)

    changelog = Marking(jira = args.url, name = args.name).generate(releases, args.format)
    print(changelog)