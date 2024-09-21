import psycopg2
import time
import html

def fetch_bookmarks():
    conn = psycopg2.connect(
        dbname="bookmarks",
        user="bookmarks",
        password="bookmarks",
        host="gmach",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT url, title, add_date, last_modified, icon, taxonomy
        FROM bookmarks
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

class Folder:
    def __init__(self, name):
        self.name = name
        self.subfolders = {}
        self.bookmarks = []

    def get_subfolder(self, name):
        if name not in self.subfolders:
            self.subfolders[name] = Folder(name)
        return self.subfolders[name]

def build_tree(rows):
    root = Folder("Bookmarks")
    for url, title, add_date, last_modified, icon, taxonomy in rows:
        if not taxonomy:
            taxonomy = "Unsorted"
        folder = root
        for part in taxonomy.split('/'):
            folder = folder.get_subfolder(part.strip())
        folder.bookmarks.append({
            'url': url,
            'title': title or url,
            'add_date': add_date,
            'last_modified': last_modified,
            'icon': icon,
        })
    return root

def write_bookmarks_html(root_folder, filename='bookmarks.html'):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!--This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
""")
        def write_folder(folder, indent=1):
            indent_str = '    ' * indent
            f.write(f"{indent_str}<DL><p>\n")
            for name, subfolder in sorted(folder.subfolders.items(), key=lambda item: item[0].lower()):
                f.write(f"{indent_str}    <DT><H3>{html.escape(name)}</H3>\n")
                write_folder(subfolder, indent + 2)
            for bookmark in sorted(folder.bookmarks, key=lambda b: b['title'].lower()):
                title = html.escape(bookmark['title'])
                url = html.escape(bookmark['url'])
                add_date = str(int(bookmark['add_date'] or time.time()))
                icon = bookmark['icon'] or ''
                icon_str = f' ICON="{html.escape(icon)}"' if icon else ''
                f.write(f"{indent_str}    <DT><A HREF=\"{url}\" ADD_DATE=\"{add_date}\"{icon_str}>{title}</A>\n")
            f.write(f"{indent_str}</DL><p>\n")
        write_folder(root_folder)
    print(f"Bookmarks exported to {filename}")

def main():
    rows = fetch_bookmarks()
    root_folder = build_tree(rows)
    write_bookmarks_html(root_folder)

if __name__ == '__main__':
    main()
