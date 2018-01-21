import wikipedia
import pickle


def explore_page(page_title, network, to_explore, inner=False, all_nodes=None):
    """
    This function explores the Wikipedia page who's title is `page_title`.
    :param page_title: title of the Wikipedia page we want to explore
    :param network: dictionary containing the nodes of the graph. If the current page is a real page, we
    add it to this dictionary.
    :param to_explore: Queue of the nodes to explore. We add all the links contained in the current page to this queue.
    :param inner: Boolean. If we're looking for inner links in the network (last step of the scraping), then there is
    no need to explore disambiguation pages or to append the links of the current page to the `to_explore` queue.
    :param all_nodes: This is the set of all the nodes in the network. It is not None only `inner` is True. This is
    useful in order to find the inner links (we take the intersection of the neighbors with the nodes of the network.
    """

    if page_title not in network.keys():
        # then this page has not been explored yet
        try:
            page = wikipedia.page(page_title)  # get the page
            title = page.original_title
            if title not in network.keys():  # check if the original title has already been explored
                if not inner:
                    network[title] = {'links': page.links, 'categories': page.categories, 'url': page.url}
                    for node in page.links:
                        to_explore.append(node)
                else:
                    links = list(set(page.links).intersection(set(all_nodes)))
                    network[title] = {'links': links, 'categories': page.categories, 'url': page.url}
        except wikipedia.DisambiguationError as e:
            if inner:
                # We are only looking for inner links, no need to explore the disambiguation page.
                return
            print('Disambiguation of : {}'.format(page_title))
            links = e.options  # those are the pages listed in the disambiguation page
            for node in links:
                    to_explore.append(node)
        except wikipedia.PageError:
            # page does not exist nothing we can do
            return
        except wikipedia.RedirectError:
            return


def save_obj(obj, name):
    with open('data/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('data/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def get_bag_of_communities(network, partition):
    """
    :param network: dictionary containing for each key (each node/page) a dictionary containing the page categories.
    :param partition: list of the community assignment
    :return: list of dictionaries, one dictionary per community. Each dictionary contains the categories of all the
    nodes of a given community as keys and the number of pages in the community that have this category as values.
    """
    k = len(set(partition))  # number of communities
    bags_of_categories = [{} for _ in range(k)]
    for i, title in enumerate(network.keys()):
        cats = network[title]['categories']
        if type(partition) == list:
            label = partition[i]
        else:
            label = partition[title]
        for c in cats:
            if c in bags_of_categories[label].keys():
                bags_of_categories[label][c] += 1
            else:
                bags_of_categories[label][c] = 1

    return bags_of_categories
