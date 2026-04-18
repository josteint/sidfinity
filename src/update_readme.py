"""Update the dashboard section in README.md from grades.db."""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hvsc_dashboard import load_sidid_full, get_engine_files, format_dashboard
from grade_db import connect, engine_summary


def update_readme():
    readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'README.md')

    # Generate dashboard text
    sidid_data = load_sidid_full()
    total_sids = len(sidid_data)
    db = connect()
    engine_grades = engine_summary(db)

    # Add engines from sidid not in DB
    all_engine_files = get_engine_files(sidid_data)
    for engine, files in all_engine_files.items():
        if engine not in engine_grades:
            engine_grades[engine] = {'ID': len(files)}

    db.close()

    dashboard = format_dashboard(engine_grades, total_sids)

    # Read README
    with open(readme_path) as f:
        content = f.read()

    # Replace between markers
    pattern = r'(<!-- BEGIN DASHBOARD -->\n```\n).*?(```\n<!-- END DASHBOARD -->)'
    replacement = r'\g<1>' + dashboard + r'```\n<!-- END DASHBOARD -->'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content != content:
        with open(readme_path, 'w') as f:
            f.write(new_content)
        print('README.md dashboard updated')
    else:
        print('README.md dashboard unchanged')


if __name__ == '__main__':
    update_readme()
