__all__ = ['Report']

import os
import shutil
import yaml 

from io import StringIO

class Report:
    def __init__(self, path_to_report):
        self.path_to_report = path_to_report
        self.report = None 

    def get_report(self):
        if self.report is None:
            self.report = self._read_report()  
        return self.report

    def _reformat_report(self, report):
        new_report = {}
        # Reformat from a List to a Dict where the key is the name
        for item in report:
            if "violations" in item.keys():
                # Only add entries that have Violations
                new_report[item['name']] = item
            # We dropped all rulesests with empty violations
        return new_report
    
    def _read_report(self):
        with open(self.path_to_report, 'r') as f:
            report = yaml.safe_load(f)
        report = self._reformat_report(report)
        return report
    
    def write_markdown(self, output_dir):
        # We will create a single directory per source app 
        # Where each ruleset with data is in its own file
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as error:
            print(f"Error creating directory {output_dir}: {error}")
            raise error
        report = self.get_report()
        # Iterate through each Ruleset that has data 
        # Write a separate file per ruleset
        for ruleset_name in report.keys():
            ruleset = report[ruleset_name]
            ruleset_name_display = ruleset_name.replace('/', '_')
            with open(f"{output_dir}/{ruleset_name_display}.md", 'w') as f:
                # We want to start each run with a clean file
                f.truncate(0)
                buffer = StringIO()
                self._get_markdown_snippet(ruleset_name, buffer)
                buffer.seek(0)
                shutil.copyfileobj(buffer, f)
                print(f"Writing {ruleset_name} to {output_dir}/{ruleset_name_display}.md")
                buffer.close()

    def _get_markdown_snippet(self, ruleset_name, f):
        report = self.get_report()
        ruleset = report[ruleset_name]
        f.write(f"# {ruleset_name}\n")
        f.write(f"## Description\n")
        f.write(f"{ruleset.get('description', '')}\n")
        f.write(f"* Source of rules: https://github.com/konveyor/rulesets/tree/main/default/generated\n")
        f.write(f"* Sample application: https://github.com/deewhyweb/eap-coolstore-monolith\n")
        f.write(f"## Violations\n")
        f.write(f"Number of Violations: {len(ruleset['violations'])}\n")
        counter = 0
        for count, key in enumerate(ruleset['violations']):
            items = ruleset['violations'][key]
            f.write(f"### #{count} - {key}\n")
            # Break out below for violation 
            # Then we can weave in an example perhaps?
            # Or should there be a Markdown class that is responsible for blending
            # . - Report
            # . - Per Violation create a prompt/run/example

            f.write(f"* Category: {items['category']}\n")
            if 'effort' in items:
                f.write(f"* Effort: {items['effort']}\n")
            f.write(f"* Description: {items['description']}\n")
            if 'labels' in items:
                f.write(f"* Labels: {', '.join(items['labels'])}\n")
            if 'links' in items:
                f.write(f"* Links\n")
                for l in items['links']:
                    f.write(f"  * {l['title']}: {l['url']}\n")
            if 'incidents' in items:
                f.write(f"* Incidents\n")
                for incid in items['incidents']:
                    #Possible keys of 'uri', 'message', 'codeSnip'
                    if 'uri' in incid:
                        f.write(f"  * {incid['uri']}\n")    
                    if 'message' in incid:
                        f.write(f"      * {incid['message']}\n")
                    if 'codeSnip' in incid:
                        f.write(f"      * Code Snippet:\n")
                        f.write(f"```java\n")
                        f.write(f"{incid['codeSnip']}\n")
                        f.write(f"```\n")

    def get_violation_snippet(self, ruleset_name, violation_name):
        report = self.get_report()
        ruleset = report[ruleset_name]
        violation = ruleset['violations'][violation_name]
        buffer = StringIO()
        buffer.write(f"# {ruleset_name}\n")
        buffer.write(f"## Description\n")
        buffer.write(f"{ruleset['description']}\n")
        buffer.write(f"* Source of rules:")
     
