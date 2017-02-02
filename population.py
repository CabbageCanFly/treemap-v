"""Modelling Population Data

=== Module Description ===
This module contains a new class, PopulationTree, which is used to model
population data drawn from the World Bank API.
Even though this data has a fixed hierarchichal structure (only three levels:
world, region, and country), because we are able to model it using an
AbstractTree subclass, we can then run it through our treemap visualisation
tool to get a nice interactive graphical representation of this data.

NOTE: You'll need an Internet connection to access the World Bank API
"""
import json
import urllib.request as request

from tree_data import AbstractTree


# Constants for the World Bank API urls.
WORLD_BANK_BASE = 'http://api.worldbank.org/countries'
WORLD_BANK_POPULATIONS = (
    WORLD_BANK_BASE +
    '/all/indicators/SP.POP.TOTL?format=json&date=2014:2014&per_page=270'
)
WORLD_BANK_REGIONS = (
    WORLD_BANK_BASE + '?format=json&date=2014:2014&per_page=310'
)


class PopulationTree(AbstractTree):
    """A tree representation of country population data.

    This tree always has three levels:
      - The root represents the entire world.
      - Each node in the second level is a region (defined by the World Bank).
      - Each node in the third level is a country.

    The data_size attribute corresponds to the 2014 population of the country,
    as reported by the World Bank.

    See https://datahelpdesk.worldbank.org/ for details about this API.
    """
    def __init__(self, world, root=None, subtrees=None, data_size=0):
        """Initialize a new PopulationTree.

        If <world> is True, then this tree is the root of the population tree,
        and it should load data from the World Bank API.
        In this case, none of the other parameters are used.

        If <world> is False, pass the other arguments directly to the superclass
        constructor. Do NOT load new data from the World Bank API.

        @type self: PopulationTree
        @type world: bool
        @type root: object
        @type subtrees: list[PopulationTree] | None
        @type data_size: int
        """
        if world:
            region_trees = _load_data()
            AbstractTree.__init__(self, 'World', region_trees)
        else:
            if subtrees is None:
                subtrees = []
            AbstractTree.__init__(self, root, subtrees, data_size)

    def get_separator(self):
        """Return the description of this node, separating
        each ancestor by '--'.

        In the visualiser, the representation would be:
        'World -- <region> -- <country>'

        @type self: PopulationTree
        @rtype: str

        >>> pt = PopulationTree(True)
        >>> leaf = pt.leaf_at((0, 0), (0, 0, 1024, 768))
        >>> leaf.get_separator()[:9]
        'World -- '
        """
        if self._parent_tree is None:
            result = self._root
        else:
            result = self._parent_tree.get_separator() + ' -- ' + self._root
        return result


def _load_data():
    """Create a list of trees corresponding to different world regions.

    Each tree consists of a root node -- the region -- attached to one or
    more leaves -- the countries in that region.

    @rtype: list[PopulationTree]
    """
    # Get data from World Bank API.
    country_populations = _get_population_data()
    regions = _get_region_data()

    # Each region tree has only two levels:
    #   - a root storing the name of the region
    #   - zero or more leaves, each representing a country in the region
    lst = []
    for region in regions:
        subtree = []
        for country in regions[region]:
            # Due to some inconsistencies in the json,
            # we have to check if the country from regions[region]
            # is a valid entry for <country_populations>.
            if country in country_populations:
                subtree.append(PopulationTree(False, country, None,
                                              country_populations[country]))
        lst.append(PopulationTree(False, region, subtree))

    return lst


def _get_population_data():
    """Return country population data from the World Bank.

    The return value is a dictionary, where the keys are country names,
    and the values are the corresponding populations of those countries.

    Ignore all countries that do not have any population data,
    or population data that cannot be read as an int.

    @rtype: dict[str, int]
    """
    # We are doing some pre-processing of the data for you.
    # The first element returned is ignored because it's just metadata.
    # The second element's first 47 elements are ignored because they aren't
    # countries.
    _, population_data = _get_json_data(WORLD_BANK_POPULATIONS)
    population_data = population_data[47:]

    countries = {}

    for country in population_data:
        if country["value"] is not None and int(country["value"]) != 0:
            countries[country['country']['value']] = int(country['value'])

    return countries


def _get_region_data():
    """Return country region data from the World Bank.

    The return value is a dictionary, where the keys are region names,
    and the values a list of country names contained in that region.

    Ignore all regions that do not contain any countries.

    @rtype: dict[str, list[str]]
    """
    # We ignore the first component of the returned JSON, which is metadata.
    _, country_data = _get_json_data(WORLD_BANK_REGIONS)

    regions = {}

    for item in country_data:
        region = item['region']['value']

        # If this key already exists in <regions>, append the country.
        # Otherwise, make a new list[str] with the given key and country.
        if region in regions:
            regions[region].append(item['name'])
        else:
            regions[region] = [item['name']]
    regions.pop("Aggregates")

    return regions


def _get_json_data(url):
    """Return a dictionary representing the JSON response from the given url.

    @type url: str
    @rtype: Dict
    """
    response = request.urlopen(url)
    return json.loads(response.read().decode())