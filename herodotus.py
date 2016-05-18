#!/usr/bin/env python3
from git import Repo
from git import Git
from operator import methodcaller
import re
import markdown

class Tag:

    template = '(?P<main_version>\\d*)\\.(?P<major_version>\\d*).(?P<minor_version>\\d*)'

    def __init__(self, git_tag):
        self.tag = git_tag
        self.match = re.search(self.template, str(git_tag))
        if self.match:
            self.main_version = self.match.group('main_version')
            self.major_version = self.match.group('major_version')
            self.minor_version = self.match.group('minor_version')
            self.name = self.main_version + "." + self.major_version + "." + self.minor_version
            
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
        
    def get_releases(self):
        tags = self.get_tags()
        releases = []
        for i in range(1, len(tags)):
            released_tag = tags[i]
            tag_before_release = tags[i-1]
            log = Git(working_dir = self.directory).log(tag_before_release.name + ".." + released_tag.name)
            issues = re.findall(self.issue_regexp, log)
            if issues:
                release = Release(released_tag.name)
                for issue in issues:
                    release.add_feature(issue)
                releases.append(release)
        return reversed(releases)
        
directory = "/Users/stCarolas/NetBeansProjects/corp-rpay-catalogs-api"
url = "http://jira/browse/"
pylog = Herodotus(directory)
releases = pylog.get_releases()

changelog = "# Version History"
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
            changelog += "* [" + issue + "]" + "(" + url + issue + ")" + "\n"

print(changelog)
# html = markdown.markdown(changelog)
# print(html)