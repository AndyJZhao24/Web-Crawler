import os
import shutil
from datetime import datetime

if not (os.path.exists('rsrc/wordFreq.json') and os.path.exists('rsrc/wordCount.json') and os.path.exists('rsrc/subDom.json') and os.path.exists('frontier.shelve')):
    print('File(s) to be backed up not found')
else:
    directory = 'Backups/' + datetime.now().strftime("%m%d%Y-%H%M%S/")
    if not os.path.exists('Backups'):
        os.mkdir('Backups')
    os.mkdir(directory)
    shutil.copy2('rsrc/wordFreq.json', directory + 'wordFreq.json')
    shutil.copy2('rsrc/wordCount.json', directory + 'wordCount.json')
    shutil.copy2('rsrc/subDom.json', directory + 'subDom.json')
    shutil.copy2('frontier.shelve', directory + 'frontier.shelve')
    print("Files backed up to " + directory)

