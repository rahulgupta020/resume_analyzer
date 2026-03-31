import os
import re

directory = r'c:\Users\Sumit Pandey\Documents\resume_analyzer\templates\resume\templates'

def get_block_end(content, start_idx):
    # This function counts opened {% if ... %} and closed {% endif %} and {% for ... %} {% endfor %}
    # wait, the block we're searching is just {% if experiences %}
    tags = re.compile(r'{%\s*(if|endif|for|empty|endfor)\b[^%]*%}')
    
    depth_if = 0
    pos = start_idx
    
    while True:
        match = tags.search(content, pos)
        if not match:
            break
            
        tag = match.group(1)
        if tag == 'if':
            depth_if += 1
        elif tag == 'endif':
            depth_if -= 1
            
        if depth_if == 0:
            return match.end()
            
        pos = match.end()
        
    return -1

def auto_patch(content, file_id):
    # Hide existing additionals
    content = content.replace('{% if additionals %}', '{% if False %}')
    
    idx = content.find('{% if experiences %}')
    if idx == -1:
        return content # no experiences block found?
        
    end_idx = get_block_end(content, idx)
    if end_idx == -1:
        return content
        
    # Attempt to extract a title class
    match = re.search(r'class="([^"]*title[^"]*|[^"]*header[^"]*|[^"]*label[^"]*)"[^>]*>Experience<', content, re.IGNORECASE)
    title_class = match.group(1).strip() if match else ""
    if not title_class:
        match = re.search(r'class="([^"]*title[^"]*|[^"]*header[^"]*|[^"]*label[^"]*)"[^>]*>\s*Work Experience', content, re.IGNORECASE)
        title_class = match.group(1).strip() if match else "sec-title"

    new_html = f"""
      <!-- Additional -->
      {{% if additionals %}}
      <div style="margin-top:20px; margin-bottom: 20px;">
        <div class="{title_class}" style="text-transform:uppercase; font-weight:bold; margin-bottom:8px;">Additional</div>
        <div>
          {{% for add in additionals %}}
          <div style="margin-bottom:12px;">
            <div style="font-weight:600;">{{{{ add.additional_title }}}}</div>
            {{% if add.additional_desc %}}
              <div style="opacity:0.85; margin-top:4px;">
                {{% for line in add.additional_desc.splitlines %}}
                  {{% if line.strip %}}<p style="margin:0 0 4px 0;">{{{{ line }}}}</p>{{% endif %}}
                {{% endfor %}}
              </div>
            {{% endif %}}
          </div>
          {{% endfor %}}
        </div>
      </div>
      {{% endif %}}

      <!-- Custom Sections -->
      {{% for custom in custom_sections %}}
      <div style="margin-top:20px; margin-bottom: 20px;">
        <div class="{title_class}" style="text-transform:uppercase; font-weight:bold; margin-bottom:8px;">{{{{ custom.title }}}}</div>
        <div>
          <div style="opacity:0.85; margin-top:4px;">
            {{% for line in custom.description.splitlines %}}
              {{% if line.strip %}}<p style="margin:0 0 4px 0;">{{{{ line }}}}</p>{{% endif %}}
            {{% endfor %}}
          </div>
        </div>
      </div>
      {{% endfor %}}
"""
    
    content = content[:end_idx] + new_html + content[end_idx:]
    return content

for i in range(2, 18):
    if i in [1, 3]: continue
    filepath = os.path.join(directory, f'template{i}.html')
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '{% for custom in custom_sections %}' in content:
        continue

    new_content = auto_patch(content, i)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
print("Templates patched successfully")
