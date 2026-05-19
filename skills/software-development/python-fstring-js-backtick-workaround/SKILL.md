---
name: python-fstring-js-backtick-workaround
description: When embedding HTML/JS with template literals in a Python f-string, both f-string and str.format() choke on brace syntax. The fix is a regular string with str.replace() for variable injection.
---

# Problem

You have a Python f-string (`html_content = f"""..."""`) that contains inline JavaScript, and the JS uses template literals with backticks:

```python
# THIS BREAKS in Python 3.11
html_content = f"""
<script>
function render(data) {
    const items = data.map(x => `<div>${x.name}</div>`).join('');
    # SyntaxError! Backtick inside f-string brace
}
</script>
"""
```

## Root Cause

- Python 3.11 f-strings do not support backticks
- JS template literals (`${...}`) look like Python f-string expressions
- `str.format()` has the same issue: both interpret `{` and `}` as delimiters
- CSS braces also need `{{ }}` escaping in f-strings, making JS backtick nesting even harder

## The Fix

Use a regular triple-quoted string with `str.replace()` for variable injection:

```python
# Step 1: Build variable dict
stats_replace = {
    "time": datetime.now().strftime('%Y-%m-%d %H:%M'),
    "count": stats.get("count", 0),
    "score": stats.get("score", 0),
}

# Step 2: Use a regular string (NOT f-string)
# No brace escaping needed at all
html_template = """
<div class="stat">
    <span class="value">{time}</span>
    <span class="count">{count}</span>
</div>
<script>
// JS template literals work fine here
function render(data) {
    const items = data.map(x => `<div>${x.name}</div>`).join('');
}
</script>
"""

# Step 3: Inject variables with str.replace()
html_content = (html_template
    .replace('{time}', stats_replace['time'])
    .replace('{count}', str(stats_replace['count']))
    .replace('{score}', str(stats_replace['score']))
)
self._send_html(html_content)
```

## Why This Works

| Approach | Braces in JS/CSS | Backticks | Verdict |
|----------|-------|--------|---------|
| `f"""..."""` | Must escape `{{ }}` | BROKEN | No |
| `""".format()` | Interprets as placeholder | OK | No |
| `string.Template` | OK with `$var` | OK | Tricky |
| **Regular + replace()** | OK | OK | **Best** |

## Pitfalls

1. **All placeholders must be replaced** or they stay as literal text. Use a dict + loop over expected keys to catch missing ones.
2. **Stringify numbers** with `str()` before replacement.
3. **Order matters** if one placeholder is a substring of another. Replace longer ones first.
4. **Avoid literal braces** in template text. Use a delimiter like `[%placeholder%]` if HTML needs literal `{`.

## Alternative: Extract HTML to File

For large JS templates, extract to a file with `%s` placeholders:

```python
with open('templates/dashboard.html') as f:
    html = f.read() % (value1, value2, value3)
```

Or use Jinja2 if available:

```python
from jinja2 import Template
html = Template(open('templates/dashboard.html').read()).render(**context)
```
