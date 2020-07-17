# Presidential Speeches

A slick way to create search engines is to index a corpus of text into a lower dimensional space then return a result 
based on the similarity of the input to the latent space of the corpus.

In this project I scrape a corpus of president's speeches given in their official capacity (relatively small corpus by
NLP standards) and map it to an LSI space with 10 dimensions where a constituent "document" is defined as a sentence of 
a speech. 

An input query is mapped to this latent space and compared to the corpus of documents (defined as sentences in
speeches). The most similar president and speech are returned (default is the top 10 most similar, but it is tunable). 
See examples below for some cool results.

![Presidents Logo](/docs/lincoln.jpg "Presidents Logo" | width=200)

## Procedure

- Python 3.5
- `cd presidents-speeches`
- `pip install -e .`

## Get Data

- `ps_download` will scrape speeches from the urls in `urls.json`
- Curate data with: `ps_curate`

## Train

- `ps_train` will train an lsi model from the corpus where constituent documents are defined as sentences in the speech.

## Predict

- `ps_predict --query "Fake News" --num_out 3` with output the top three presidents and speeches most similar to the 
input query.

Example: 
```
> ps_predict --query "Fake News" --num_out 3
{
    'Fake News': {
        'presidents': ['trump', 'clinton', 'obama'], 
        'presidents_sim': [3.991385757923126, 3.9502575993537903, 3.949316680431366], 
        'speeches': [
            'https://millercenter.org/the-presidency/presidential-speeches/february-23-2018-remarks-conservative-political-action', 
            'https://millercenter.org/the-presidency/presidential-speeches/july-24-2017-speech-boy-scout-jamboree', 
            'https://millercenter.org/the-presidency/presidential-speeches/october-6-1996-presidential-debate-senator-bob-dole'
        ],
        'speeches_sim': [3.976735532283783, 3.9579113721847534, 3.949946939945221], 
    }
}

> ps_predict --query "Vietnam civil rights" --num_out 3

{
    'Vietnam civil rights': {
        'presidents': ['kennedy', 'johnson', 'polk'], 
        'presidents_sim': [3.95937043428421, 3.9589781761169434, 3.953145384788513],
        'speeches': [
            'https://millercenter.org/the-presidency/presidential-speeches/december-5-1848-fourth-annual-message-congress', 
            'https://millercenter.org/the-presidency/presidential-speeches/december-8-1885-first-annual-message', 
            'https://millercenter.org/the-presidency/presidential-speeches/december-5-1899-third-annual-message'
        ], 
        'speeches_sim': [3.9500176906585693, 3.947575271129608, 3.9452045559883118]
    }
}

```