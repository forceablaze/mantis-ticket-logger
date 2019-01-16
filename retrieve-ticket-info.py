#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from mantis_utils.mantis.Connector import Connector
from mantis_utils.mantis.IssueViewer import IssueViewer

from optparse import OptionParser
from pathlib import Path

import json
import datetime
import functools
print_flush = functools.partial(print, flush=True)

def viewIssue(connector, issue, date):
    print_flush(issue)
    viewer = IssueViewer(issue)

    # remove time zone info
    timeStr = viewer.getSubmittedDate().strftime("%Y%m%d%H%M%S")
    issueTime = datetime.datetime.strptime(timeStr, '%Y%m%d%H%M%S')

    if date is not None and issueTime < date:
        print_flush(
            'Issue {} last updated time < {}, ignore it'.format(viewer.getId(), date))
        return

    jsonObj = {}

    print_flush('IssueId: {}\n' \
          'state: {}\n' \
          'category: {}\n' \
          'Reporter: {} ({}), {}\n' \
          'last updated time: {}\n' \
          'submitted time: {}\n' \
          'Description: {}'.format(
            viewer.getId(),
            viewer.getStatusName(),
            viewer.getCategory(),
            viewer.getReporterName(),
            viewer.getReporterRealName(),
            viewer.getReporterEmail(),
            viewer.getLastUpdatedTime(),
            viewer.getSubmittedDate(),
            viewer.getDescription()))

    jsonObj['issue_id'] = viewer.getId()
    jsonObj['state'] = viewer.getStatusName()
    jsonObj['category'] = viewer.getCategory()
    jsonObj['reporter'] = {}
    jsonObj['reporter']['id'] = viewer.getReporter()['id']
    jsonObj['reporter']['name'] = viewer.getReporterName()
    jsonObj['reporter']['real_name'] = viewer.getReporterRealName()
    jsonObj['reporter']['email'] = viewer.getReporterEmail()
    jsonObj['last_updated_time'] = str(viewer.getLastUpdatedTime())
    jsonObj['submitted_time'] = str(viewer.getSubmittedDate())
    jsonObj['description'] = viewer.getDescription()

    attachments = viewer.getAttachments()
    if attachments is not None:
        pass
    else:
        pass

    notes = viewer.getNotes()
    if notes is not None:
        jsonObj['notes'] = []

    for note in notes:
        newNote = {}
        newNote['id'] = note['id']
        newNote['reporter'] = {}
        newNote['reporter']['id'] = note['reporter']['id']
        newNote['reporter']['name'] = note['reporter']['name']
        newNote['reporter']['real_name'] = note['reporter']['real_name']
        newNote['reporter']['email'] = note['reporter']['email']
        newNote['text'] = note['text']
        newNote['last_modified'] = str(note['last_modified'])
        newNote['date_submitted'] = str(note['date_submitted'])

        print_flush('id: {}\nreporter: {} ({}) {}\ntext: {}' \
          'last updated time: {}\n' \
          'submitted time: {}\n'.format(
            note['id'],
            note['reporter']['name'],
            note['reporter']['real_name'],
            note['reporter']['email'],
            note['text'],
            note['last_modified'],
            note['date_submitted']
        ))

        jsonObj['notes'].append(newNote)

    text = json.dumps(jsonObj, ensure_ascii=False, indent=4)
    print_flush(text)

    outputFolder = Path('output', viewer.getProjectName())
    outputFolder.mkdir(parents=True, exist_ok=True)

    with open(Path(outputFolder, str(viewer.getId())), 'w') as f:
        f.write(text)

def mainEntry(url, username, password, projectName = None,
        time = None, issueId = None):
    connector = Connector(url, username, password)
    connector.connect()


    if issueId is not None:
        issue = connector.getIssue(issueId)
        viewIssue(connector, issue, time)
    elif projectName is not None:
        projectId = connector.getProjectId(projectName)
        print_flush("ProjectId: " + str(projectId))

        issues = connector.getProjectIssues(projectId)
        for issue in issues:
            print_flush('Found issue:')
            viewIssue(connector, issue, time)


if __name__ == '__main__':
    parser = OptionParser()  

    parser.add_option("-U", "--url", type = "string",
        action="store", dest = "url",
        help = "The url of mantis SOAP API")

    parser.add_option("-i", "--issueId", default = None,
        action = "store", dest = "issueId",
        help = "Mantis Issue id")

    parser.add_option("-P", "--project", default = None,
        action = "store", dest = "project",
        help = "Mantis Project name")

    parser.add_option("-u", "--username",
        action = "store", dest = "username",
        help = "Mantis username")

    parser.add_option("-p", "--password",
        action = "store", dest = "password",
        help = "Mantis password")

    parser.add_option("-f", "--from-time", default = None,
        action = "store", dest = "time",
        help = "the issue time searching from, format yyyyMMddHHmmss")

    (options, args) = parser.parse_args()  

    if options.time is not None:
        dateSearchFrom = datetime.datetime.strptime(options.time, '%Y%m%d%H%M%S')
    else:
        dateSearchFrom = None

    mainEntry(url = options.url,
            projectName = options.project,
            issueId = options.issueId,
            username = options.username,
            password = options.password,
            time = dateSearchFrom)
