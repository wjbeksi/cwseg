## Chinese Word Segmenter and Lexicon Builder (CWSEG)

Chinese text processing requires the detection of word boundaries. This is a 
non-trivial step because Chinese does not contain explicit whitespace between 
words. Existing word segmentation techniques make use of precompiled 
dictionaries and treebanks. The creation of dictionaries and treebanks is a 
labor-intensive process and consequently they are updated infrequently. 
Furthermore, due to their static nature, dictionaries and treebanks lack the 
latest words that enter the lexicon.

CWSEG [1] leverages content on the Internet to build a bootstrapping Chinese 
word segmenter. Lexicon building works by employing an HTML parser. Chinese 
words parsed from webpages are stored in a dictionary. This dictionary is 
persistent and is read in upon startup. Words are stored along with their 
frequencies in the dictionary. Support is included for pruning the dictionary of 
words that fall below a given threshold. The segmenter uses the dictionary along 
with a maximum matching algorithm in order to determine word boundaries. 

## Usage

### Building a Corpus and Lexicon Dictionary
Lexicon building is done through a feed of HTML pages. A web crawler capable of 
processing millions of URIs, such as Heritrix [2], is a necessary prerequisite 
for generating a suitable lexicon dictionary.

The lexicon builder consists of an HTML parser that can tokenize a string of 
Chinese text based on suitable heuristics. Lexicon building is persistent as 
tokenized words are saved to a dictionary. The dictionary is written to disk 
when the program exits and is available upon start up the next time the lexicon 
builder is instantiated.

To build a lexicon dictionary run

    $ python html_feeder.py -l lex_dict.p -m 16 -d html_files

where 'lex_dict.p' is the name of the lexicon dictionary, '16' is the maximum 
word length, and 'html_files' is a directory of crawled HTML files containing 
Chinese text.

Statistics included in the lexicon dictionary are the word frequencies of each 
entry. When a new word is added to the dictionary its frequency is set to one. 
Additional occurrences of the word bump the frequency count for that word entry. 
By keeping track of the word frequency we can use frequency based heuristics 
when segmenting words. It also allows for a heuristic based mechanism for 
removing low frequency words, which could indicate false positives, from the 
dictionary.

To show statistics on word frequency patterns run

    $ python segmenter.py -i -l lex_dict.p

where 'lex_dict.p' is the previously built lexicon dictionary.

### Chinese Word Segmentation

To perform word segmentation run

    $ python segmenter.py -l lex_dict.p -s file_to_segment

where 'lex_dict.p' is the lexicon dictionary of Chinese words mined from HTML 
files and 'file_to_segment' is a UTF-8 encoded file of Chinese text.

## References

[1] W.J. Beksi, "A Web-based Approach To Chinese Word Segmentation," 
Proceedings of the 14th International Conference on the Processing of East 
Asian Languages (ICPEAL), Nagoya, Japan, 2012.

[2] Heritrix: https://webarchive.jira.com/wiki/display/Heritrix
