import pandas as pd
import re
import json
import sys

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)

def format_abbreviations(text):
   text = re.sub(r'var\.', 'variation', text) # need to account for cases like... var. VF
   text = re.sub(r'cf\.', 'confer', text)
   text = re.sub(r'Cf\.', 'Confer', text)
   # include space to avoid entries that end in e.g. 'edge chip.'
   text = re.sub(r'p\. ', 'page ', text) 
   text = re.sub(r'rev\. ', 'reverse ', text)
   text = re.sub(r'obv\. ', 'obverse ', text)
   text = re.sub(r'corr\. ', 'correction ', text)
   text = re.sub(r'pl\.', 'proof like ', text)
   return text

def format_emperor(text, verbose=False):
   emperors = [
      'Augustus',
      'Tiberius',
      'Gaius',
      'Agrippina Senior',
      'Nero',
      'Vespasian',
      'Titus',
      'Domitian',
      'Julia Titi',
      'Antoninus Pius', 
      'Faustina Senior'
   ]
   for emperor in emperors:
      if emperor in text.split('. ')[0]:
         text = re.sub(emperor, 'Emperor: '+emperor, text, 1) # first match
         return text
   raise Exception('No emperor match in text: {}'.format(text))

def format_reign(text):
   # print('----------------------')
   # print(text)
   regexps = [
      r'Died\sAD\s\d+',
      r'Died\s\d+\sAD', # AD scheme (Agrippina)
      r'\d+\sBC-AD\s\d+',
      r'AD\s\d+-\d+',
      r'\d+-\d+\sAD' # alternative AD scheme
   ]
   for regexp in regexps:
      result = re.search(regexp, text)
      if result is not None:
         result = result.group() # return the match
         text = re.sub(result, 'Reign: '+result, text, 1) # first match
         # print('---->', text)
         return text
   raise Exception('No regex match for reign in text: {}'.format(text))

def format_denomination(text):
   #denominations = [r'AV Aureus', r'AR Denarius', r'AR Cistophorus', r'(Æ|AE) Sestertius']
   text = re.sub(r'AV Aureus', 'Denomination: AV Aureus.', text)
   text = re.sub(r'AR Denarius', 'Denomination: AR Denarius.', text)
   text = re.sub(r'AR Cistophorus', 'Denomination: AR Cistophorus.', text)
   text = re.sub(r'(Æ|AE) Sestertius', 'Denomination: AE Sestertius.', text)
   return text

def format_measurements(text, verbose=False):
   if verbose:
      print('------------------------------------------------------')
      print(text)
   regexps = [
      r'\(.+mm.+gm?.+h\)\.?', # case 0: complete string (sometimes final . is missing)
      r'\(.+mm.+gm?\)\.',     # case 1: missing 'h' only
      r'\(.+mm\)\.',          # case 2: missing 'g' and 'h' (no end space)
      r'\(.+gm?.+\d+h\)\.',   # case 3: missing 'mm' only
      r'\(.+mm \)\.',         # case 4: missing 'g' and 'h' (with ending space)
      r'\(\S+\s+gm?\s?\)\.',  # case 5: missing 'mm' and 'h'; using \S and \s
      r'\(\d+mm\s+\d+h\)\.',  # case 6: missing 'g' only
      r'\(\)\.'               # case 7: missing all three
   ]
   for case, regexp in enumerate(regexps):
      if verbose:
         print('case {}'.format(case))
         print('regexp: {}'.format(regexp))
      result = re.search(regexp, text)
      if result is not None:
         # print(result)
         result = result.group(0)
         if verbose:
            print('match: {}'.format(result))
         # consolidate measurement variations
         result = result.replace('  g', ' g')
         result = result.replace(' g', 'g')
         # variation 'gm' occasionally present
         result = result.replace('  gm', ' gm')
         result = result.replace(' gm', 'gm')
         result = result.replace('gm', 'g')
         # remove initial spaces
         result = result.replace(' mm', 'mm')
         result = result.replace(' h', 'h')
         # remove final spaces
         result = result.replace('h ', 'h')
         # remove brackets and final period '.'
         result = result[1:-2]
         if verbose:
            print(result)
         # replace internal '.'s to simplify later feature extraction
         result = result.replace('.', '@')
         if verbose:
            print(result)
         # split match into individual measurements
         result = result.split(' ')
         if verbose:
            print(result)
         # denote missing fields as unlisted
         if case==0:
            pass
         if case==1:
            result.insert(2, 'unlisted')
         if case==2:
            result.insert(1, 'unlisted')
            result.insert(2, 'unlisted')
         if case==3:
            result.insert(0, 'unlisted')
         if case==4:
            result.insert(1, 'unlisted')
            result.insert(2, 'unlisted')
         if case==5:
            result.insert(0, 'unlisted')
            result.insert(2, 'unlisted')
         if case==6:
            result.insert(1, 'unlisted')
         if case==7:
            result.insert(0, 'unlisted')
            result.insert(1, 'unlisted')
            result.insert(2, 'unlisted')
         if verbose:
            print(result)
         # insert keyword for each measurement type
         result[0] = result[0].replace(result[0], 'Diameter: '+result[0]+'.')
         result[1] = result[1].replace(result[1], 'Weight: '+result[1]+'.')
         result[2] = result[2].replace(result[2], 'Hour: '+result[2]+'.')
         # rejoin the list intro a string
         new_result = ' '.join(result)
         if verbose:
            print(new_result)
         # substitute the formatted string into the original text
         text = re.sub(regexp, new_result, text)
         if verbose:
            print(text)
         return text
   raise Exception('No regex match for measurements in text: \n{}'.format(text))

def format_mint(text):
   # print(text)
   # first, check if 'mint' keyword is present, if not, add it in
   if re.search(r'[Mm]int', text) is None:
      # 1st attempt: careful, this relies on 'Hour' existing... does this make sense? When would Hour: be without \dh?
      text = re.sub(r'Hour\.', 'Hour. Mint: unlisted mint.', text) 
      # 2nd attempt when Hour is unlisted
      text = re.sub(r'Hour: unlisted\.', 'Hour: unlisted. Mint: unlisted mint.', text) 
      # 3rd attempt when Hour is defined
      if re.search(r'Hour: \dh\.', text) is not None: 
         x = re.search(r'Hour: \dh\.', text).group()
         text = re.sub(x, x+' Mint: unlisted mint.', text) 
      return text
   # if so, then break text apart on  '.', find the mint segment, 
   # put 'Mint: ' at the front, sew it back together
   segments = []
   isFound = False
   for seg in text.split('. '):
      if re.search(r'[Mm]int', seg) is not None:
         seg = 'Mint: ' + seg
         isFound = True
      segments.append(seg)
   text = '. '.join(segments)
   if not isFound:
      raise Exception('mint keyword not found in text: {}'.format(text)) 
   return text

def format_moneyer(text):

   # first, check if 'moneyer' keyword is present
   # sometimes, e.g.: Rome mint; C. Sulpicius Platorinus triumvir monetalis
   if re.search(r'[Mm]oneyer|[Mm]onetalis', text) is None:
      segments = []
      # find mint segment and append moneyer after it
      # need to handle cases like: 'Uncertain mint in Syria.', and 'Rome mint', etc.
      for seg in text.split('. '):
         result = re.search(r'[Mm]int', seg)
         if result is not None:
            seg = seg + '. Moneyer: unlisted moneyer'
         segments.append(seg)
      text = '. '.join(segments)
      return text

   # otherise...
   # mint with semicolon (or period) indicates proceeding moneyer
   # e.g. Rome mint; C. Marius C. f. moneyer.
   # want to break this apart into two fields: "Rome mint"., "C Marius C f moneyer".
   result = re.search(r'[Mm]int[ \.;].+([Mm]oneyer|[Mm]onetalis)', text) # space, dot, or semi-colon follow mint
   if result is None:
      return text

   #print('before: ', text)
   result = result.group()
   # first change 'mint.' or 'mint' to 'mint;' 
   result = re.sub(r'mint ', 'mint; ', result)
   result = re.sub(r'mint\. ', 'mint; ', result)
   # then remove any dot (.) in moneyer's name
   result = re.sub(r'\.', '', result)
   # then return the dot to mint
   result = re.sub(r'mint;', 'mint.', result)
   # finally, sub the cleaned mint & moneyer sections back into the text
   text = re.sub(r'[Mm]int[ \.;].+([Mm]oneyer|[Mm]onetalis)', result, text)

   # add 'Moneyer:' tag
   segments = []
   for seg in text.split('. '):
      if re.search(r'([Mm]oneyer|[Mm]onetalis)', seg) is not None:
         seg = 'Moneyer: ' + seg
      segments.append(seg)
   text = '. '.join(segments)
   #print('after: ', text)

   return text

def format_strike(text):
   # check for keyword
   result = re.search(r'Struck', text, 1)
   if result is not None:
      result = result.group()
      text = re.sub(result, result+':', text)
      return text
   # if keyword not present, return unlisted
   text = re.sub(r'Mint:', 'Struck: unlisted. Mint:', text) # careful, this relies on 'Mint:' existing
   return text

def format_obverse_reverse(text):
   segments = []
   is_found = False
   for seg in text.split('. '):
      if re.search(r' / ', seg) is not None:
         if(len(seg.split(' / '))!=2):
            raise Exception('more than one split in text: {}'.format(text))
         seg = 'Obverse: ' + seg
         seg = re.sub(r' / ', '. Reverse: ', seg)
         is_found = True
      segments.append(seg)
   text = '. '.join(segments)
   return text

def format_RIC(text):
   if re.search(r'RIC', text) is None:
      raise Exception('RIC keyword not found in text: {}'.format(text)) 
   text = re.sub(r'RIC', 'RN: RIC', text)
   return text

def format_grade_new(text):
   # introduce 'Grade' keyword
   segments = []
   isFound = False
   for seg in text.split('. '):
      # skip the obv/rev segments to avoid potential mismatch w/ AVG, RVFVS, etc.
      if ('Obverse:' in seg) or ('Reverse:' in seg): 
         segments.append(seg)
         continue
      if re.search(r'FDC|EF|VF|Fine|Fair', seg) is not None:
         seg = 'Grade: ' + seg
         isFound = True
      segments.append(seg)
   if not isFound:
      raise Exception('Grade not found in text: {}'.format(text))
   text = '. '.join(segments)
   # introduce 'Comments' section
   text = re.sub(r' FDC\.?', ' FDC. Comments:', text)
   text = re.sub(r' EF\.?', ' EF. Comments:', text)
   text = re.sub(r' VF\.?', ' VF. Comments:', text)
   text = re.sub(r' Fine\.?', ' Fine. Comments:', text)
   text = re.sub(r' Fair\.?', ' Fair. Comments:', text)
   return text


# this needs work
# def format_grade_new3(text):
#    print('-------------------------')

#    print(text)

#    # find first occurance of grade --> introduce 'Grade' keyword
#    # order matters here
#    grades = ['FDC', 'Choice EF', 'Superb EF', 'Near EF', 'EF', 'Choice VF', 'Nice VF', 'Good VF', 'Near VF', 'VF', 'Good Fine', 'Near Fine', 'Fine', 'Fair']
#    result = None
#    for grade in grades:
#       raw = r'{}'.format(grade)+r'[/. ]'
#       if re.search(raw, text) is not None:
#          result = grade
#          break
#    if result is None:
#       raise Exception('grade not found in text: {}'.format(text))

#    # remove the identified grade segment from the text
#    text = re.sub(result, '', text)

#    # introduce 'Grade' keyword
#    if '.' not in result:
#       result = result + '.'
#    result1 = 'Grade: ' + result
#    print(result1)

#    # find the comments section
#    comm = text.split('. ')[-1]
#    print(comm)

#    # remove the final segment
#    text = re.sub(comm, '', text)

#    # introduce 'Comments' keyword
#    result2 = 'Comments: ' + comm
#    print(result2)

#    # append everything
#    text = text + result1 + result2
#    print(text)

#    return text


if __name__ == '__main__':

   print('Running: {}'.format(sys.argv[1]))
   file_data = sys.argv[1]
   file_edge_cases = sys.argv[2]

   if (file_data is None) or (file_edge_cases is None):
      raise Exception('missing input file: {}'.format(argv))

   # Select Data
   # ===========

   df = pd.read_csv(file_data)
   print('selection: {}'.format(df.shape))

   stop_words = []
   with open('config/stop_words.txt', mode='r', encoding='utf-8') as f:
      # drop trailing \n for each line and skip lines that start with #
      stop_words = [re.compile(line[:-1]) for line in f if '#' not in line]
   #print(stop_words)
   for stop in stop_words:
      # if df[df['Description'].str.contains(stop, regex=True)].shape[0] > 0:
      #    print('-------------')
      #    print('{}\n: {}'.format(stop, df[df['Description'].str.contains(stop, regex=True)]['Description']))
      df = df[~df['Description'].str.contains(stop, regex=True)]
      #print(stop, df.shape)
   print('selection: {}'.format(df.shape))

   # remove "Affiliated Auctions"
   df = df[~df['Auction Type'].str.contains(r'Affiliated Auction')]
   print('selection: {}'.format(df.shape))

   # remove non-standard denomination
   df = df[~df['Description'].str.contains('Silver')]
   print('selection: {}'.format(df.shape))

   # Format Edge Cases
   # =================

   with open(file_edge_cases) as f: 
      data = json.load(f)
      for file, replacements in data['file'].items(): 
         for r in replacements: 
            #print(' --> replacing [{}] with [{}] from {}'.format(r['regexp'], r['sub'], file))
            df['Description'] = df['Description'].apply(lambda x: re.sub(r['regexp'], r['sub'], x))

   # Standardize Data
   # ================

   df['Auction ID'] = df['Auction ID'].astype(str)
   df['Header'] = df['Header'].apply(lambda x: 'No Header' if pd.isnull(x) else x)
   df['Notes'] = df['Notes'].apply(lambda x: 'No Notes' if pd.isnull(x) else x)

   # Standardize the Description field
   # =================================

   df['Description'] = df['Description'].apply(lambda x: format_abbreviations(x))
   df['Description'] = df['Description'].apply(lambda x: format_emperor(x))
   df['Description'] = df['Description'].apply(lambda x: format_reign(x))
   df['Description'] = df['Description'].apply(lambda x: format_denomination(x))
   df['Description'] = df['Description'].apply(lambda x: format_measurements(x))
   df['Description'] = df['Description'].apply(lambda x: format_mint(x))
   df['Description'] = df['Description'].apply(lambda x: format_moneyer(x))
   df['Description'] = df['Description'].apply(lambda x: format_strike(x))
   df['Description'] = df['Description'].apply(lambda x: format_obverse_reverse(x))
   df['Description'] = df['Description'].apply(lambda x: format_RIC(x))
   df['Description'] = df['Description'].apply(lambda x: format_grade_new(x))
   #print(df.info())

   # save intermediate result
   df.to_csv(file_data.replace('.csv', '_cleaned.csv'), index=False)

   # Extract Content from Description
   # ================================

   def extract_feature(text, keyword):
      for segment in text.split('. '):
         if keyword in segment:
            # remove keyword and clean up
            segment = segment.replace(keyword+': ', '')
            segment = segment.replace('@', '.') # hack for measure fields
            segment = segment.strip()
            return segment
      raise Exception('{} not found in {}'.format(keyword, text))

   df['Emperor'] = df['Description'].apply(lambda x: extract_feature(x, 'Emperor'))
   df['Reign'] = df['Description'].apply(lambda x: extract_feature(x, 'Reign'))
   df['Denomination'] = df['Description'].apply(lambda x: extract_feature(x, 'Denomination'))
   df['Diameter'] = df['Description'].apply(lambda x: extract_feature(x, 'Diameter'))
   df['Weight'] = df['Description'].apply(lambda x: extract_feature(x, 'Weight'))
   df['Hour'] = df['Description'].apply(lambda x: extract_feature(x, 'Hour'))
   df['Mint'] = df['Description'].apply(lambda x: extract_feature(x, 'Mint'))
   df['Moneyer'] = df['Description'].apply(lambda x: extract_feature(x, 'Moneyer'))
   df['Struck'] = df['Description'].apply(lambda x: extract_feature(x, 'Struck'))
   df['Obverse'] = df['Description'].apply(lambda x: extract_feature(x, 'Obverse'))
   df['Reverse'] = df['Description'].apply(lambda x: extract_feature(x, 'Reverse'))
   df['RIC'] = df['Description'].apply(lambda x: extract_feature(x, 'RN'))
   df['Grade'] = df['Description'].apply(lambda x: extract_feature(x, 'Grade'))
   df['Comments'] = df['Description'].apply(lambda x: extract_feature(x, 'Comments'))

   # drop the now fully parsed 'Description' field
   df.drop(['Description'], inplace=True, axis=1)
   #print(df.info())

   # save the final result
   df.to_csv(file_data.replace('.csv', '_prepared.csv'), index=False)
