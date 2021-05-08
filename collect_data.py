import newspaper, os, pickle, uuid, json
import numpy as np

datapath = "rawdata"

def load_config(configfile):
        if os.path.exists(configfile):
                with open(configfile, 'rb') as handle:
                        config = pickle.load(handle)
        else:
                config = {}
        return config

def save_config(configfile, config):
        with open(configfile, 'wb') as handle:
                pickle.dump(config, handle, protocol=pickle.HIGHEST_PROTOCOL)

def news_sources():
        return ['nytimes.com', 'cnn.com', 'bbc.com', 'latimes.com', 'chicago.suntimes.com', 'startribune.com']

def data_file_name(source):
        dirname = datapath + '/' + source
        if not os.path.exists(dirname):
                os.mkdir(dirname)
        return '{}/{}.json'.format(dirname, str(uuid.uuid4()))

def load_more_stories(urls):
        for source in news_sources():
                result = []
                paper = newspaper.build('http://' + source,
                                        language='en',
                                        memoize_articles=False)
                article_urls = [article for article in paper.articles]
                selected = np.random.choice(article_urls, 30)
                for article in selected:
                        if article.url in urls:
                                # skip an article if we have seen it
                                continue
                        try:
                                article.download()
                                article.parse()
                                result_article = {'text': article.text, 'title': article.title,
                                                  'authors': article.authors, 'url': article.url}
                                urls[article.url] = 1
                        except:
                                continue
                        # If there is no text, then skip this article.
                        if result_article["text"] == "":
                                continue

                        with open(data_file_name(source), 'w') as outfile:
                                json.dump(result_article, outfile)

        return urls


if __name__ == "__main__":
        configfile = "visitedurls.pickle"
        urls = load_config(configfile)
        urls = load_more_stories(urls)
        save_config(configfile, urls)
