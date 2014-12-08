"""Methods for computing microbial diversity indices

The basis for this library comes from Gevers et al. 2014
(http://www.ncbi.nlm.nih.gov/pubmed/24629344) in which a microbial dysbiosis
index was created based on observed increases and decreases in organisms with
respect to Crohn's disease.
"""

from __future__ import division

from numpy import log, nan


def compute_index(table, increased, decreased, key):
    """Compute a per-sample index

    Parameters
    ----------
    table : biom.Table
        A biom table that has information associated with `key`, such as
        taxonomy.
    increased : set
        A set of items that have been observed to have increased
    decreased : set
        A set of items that have been observed to have decreased
    key : str
        The metadata key to use for the computation of the index.

    Raises
    ------
    KeyError
        If the key isn't present
    ValueError
        If none of the increased or decreased items exist in the table

    Notes
    -----
    Yields `nan` if both the decreased count is 0.

    Returns
    -------
    generator
        (sample_id, index_score)
    """
    if key not in table.metadata(axis='observation')[0]:
        raise KeyError("%s is not present" % key)

    inc_f = lambda v, i, md: set(md[key]) & increased
    dec_f = lambda v, i, md: set(md[key]) & decreased
    inc_t = table.filter(inc_f, axis='observation', inplace=False)
    dec_t = table.filter(dec_f, axis='observation', inplace=False)

    if inc_t.is_empty():
        raise ValueError("None of the increased items were found")

    if dec_t.is_empty():
        raise ValueError("None of the decreased items were found")

    ids_in_common = set(inc_t.ids()) & (set(dec_t.ids()))

    for id_ in ids_in_common:
        inc_count = inc_t.data(id_, dense=False).sum()
        dec_count = dec_t.data(id_, dense=False).sum()

        if dec_count == 0:
            yield (id_, nan)
        else:
            yield (id_, log(inc_count / dec_count))
