import json
import os
from datetime import datetime

NUM_RESULTS = 50

if not (os.path.exists('rsrc/wordFreq.json') and os.path.exists('rsrc/wordCount.json') and os.path.exists('rsrc/subDom.json')):
    print('File(s) not found')
else:
    with open('rsrc/wordFreq.json', 'r') as infile:
        wordFreq = json.load(infile)
    with open('rsrc/wordCount.json', 'r') as infile:
        wordCount = json.load(infile)
    with open('rsrc/subDom.json', 'r') as infile:
        subDom = json.load(infile)
    
    filename = 'Reports/Report-' + datetime.now().strftime("%m%d%Y-%H%M%S") + '.txt'
    report = open(filename, 'w')
    report.write('Total number of unique URLs crawled: ' + str(len(wordCount)))
    print('Total number of unique URLs crawled: ' + str(len(wordCount)))
    report.write('\n\nPage with most words:\n\n')
    print('\nPage with most words:\n')
    for k, v in sorted(wordCount.items(), key = lambda x: x[1], reverse = True):
        report.write('\tURL:\t' + k + '\n')
        report.write('\tWords:\t' + str(v) + '\n')
        print('\tURL:\t' + k)
        print('\tWords:\t' + str(v))
        break

    report.write('\n\n' + str(NUM_RESULTS) + ' most common words across crawled pages:\n\n')
    print('\n' + str(NUM_RESULTS) + ' most common words across crawled pages:\n')
    count = 1
    for k, v in sorted(wordFreq.items(), key = lambda x: x[1], reverse = True):
        report.write('\t' + str(count) + '.\t' + k + ': ' + str(v) + '\n')
        print('\t' + str(count) + '.\t' + k + ': ' + str(v))
        count += 1
        if count > NUM_RESULTS:
            break

    report.write('\n\nSubdomains found in ICS and total page occurances:\n\n')
    print('\nSubdomains found in ICS and total page occurances:\n')
    occurances = 0
    for subdomain, count in sorted(subDom.items(), key = lambda x: x[1], reverse = True):
        report.write('\t' + subdomain + ': '+ str(count) + '\n')
        print('\t' + subdomain + ': ' + str(count))
        occurances += count
    report.write('\n\tUnique Subdomains found: ' + str(len(subDom)))
    report.write('\n\tTotal Page Occurances:   ' + str(occurances) + '\n')
    print('\n\tUnique Subdomains found: ' + str(len(subDom)))
    print('\tTotal Page Occurances:   ' + str(occurances))


    report.close()
    print("\nResults saved to: " + filename)
