import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    prob = 1
    # iterate through all people
    for person in people:
        # if person has no listed parents
        if people[person]["mother"] is None or people[person]["father"] is None:
            # take their probability from the unconditional distribution, multiply by conditional probability of having
            # the trait or not based on the genotype
            if person in one_gene:
                prob *= PROBS["gene"][1]
                prob = trait_prob(prob, 1, person, have_trait)
            elif person in two_genes:
                prob *= PROBS["gene"][2]
                prob = trait_prob(prob, 2, person, have_trait)
            else:
                prob *= PROBS["gene"][0]
                prob = trait_prob(prob, 0, person, have_trait)
        # otherwise, create a set of the two parent genotypes
        else:
            parents = set()
            if people[person]["mother"] in one_gene:
                parents.add(1)
            elif people[person]["mother"] in two_genes:
                parents.add(2)
            else:
                parents.add(0)

            if people[person]["father"] in one_gene:
                parents.add(1)
            elif people[person]["father"] in two_genes:
                parents.add(2)
            else:
                parents.add(0)

            # call function first to update probability of having the genotype of interest
            # then call function to update based on having the trait or not conditional on the genotype
            if person in one_gene:
                prob = inheritance(prob, 1, parents)
                prob = trait_prob(prob, 1, person, have_trait)
            elif person in two_genes:
                prob = inheritance(prob, 2, parents)
                prob = trait_prob(prob, 2, person, have_trait)
            else:
                prob = inheritance(prob, 0, parents)
                prob = trait_prob(prob, 0, person, have_trait)
    return prob


def trait_prob(prob, n_gene, person, have_trait):
    """
    This function updates the current probability estimate by multiplying the existing estimate by the probability of
    having the gene (or not, depending on the person's presence in the have_trait set) conditional on having n_gene
    alleles of the mutated gene
    """
    if person in have_trait:
        prob *= PROBS["trait"][n_gene][True]
    else:
        prob *= PROBS["trait"][n_gene][False]
    return prob


def inheritance(prob, n_gene, parents):
    """
    This function calculates the conditional probabilities of having the genotype of interest (n_gene copies)
    based on the genotypes of the parents, input as the set parents
    """
    # rename constants for ease of typing; initialize dictionary to store conditional probabilities
    pmut = PROBS["mutation"]
    pnomut = 1 - pmut
    hered_prob = dict()

    # go through each combination of the parental genotypes
    if parents == {2, 2}:
        # to get AA, must have no mutations; aa, must have two mutations; Aa, must have mutation in either allele
        hered_prob["AA"] = pnomut * pnomut
        hered_prob["Aa"] = 2 * pnomut * pmut
        hered_prob["aa"] = pmut * pmut
    elif parents == {1, 2}:
        # must consider which allele the heterozygous parent gives in addition to mutations
        # AA can arise from both parents giving A or one parent giving a with a mutation;
        # aa can arise from one parent giving a and one giving A with a mutation or A and A with 2 mutations
        # Aa can arise from Aa with no mutations, AA with one mutation in either allele, or aA with two mutations
        hered_prob["AA"] = 0.5 * pnomut * pnomut + 0.5 * pnomut * pmut
        hered_prob["Aa"] = 0.5 * pnomut * pnomut + pnomut * pmut + 0.5 * pmut * pmut
        hered_prob["aa"] = 0.5 * pnomut * pmut + 0.5 * pmut * pmut
    elif parents == {1, 1}:
        # now we must consider the probabilities from a monohybrid cross and mutations:
        # before considering mutations, P(AA) = P(aa) = 0.25, P(Aa) = 0.5
        # AA can arise from AA with no mutations, Aa with one mutation, or aa with two mutations
        # aa can arise from aa with no mutations, Aa with one mutation, or AA with two mutations
        # Aa can arise from Aa with no mutations, Aa with two mutations, or AA and aa with one mutation in either allele
        hered_prob["AA"] = 0.25 * pnomut * pnomut + 0.25 * pmut * pmut + 0.5 * pmut * pnomut
        hered_prob["Aa"] = 0.5 * pnomut * pnomut + 0.5 * pmut * pmut + pnomut * pmut
        hered_prob["aa"] = 0.25 * pnomut * pnomut + 0.25 * pmut * pmut + 0.5 * pmut * pnomut
    elif parents == {1, 0}:
        # this case is the reverse of {1, 2}
        hered_prob["AA"] = 0.5 * pnomut * pmut + 0.5 * pmut * pmut
        hered_prob["Aa"] = 0.5 * pnomut * pnomut + pnomut * pmut + 0.5 * pmut * pmut
        hered_prob["aa"] = 0.5 * pnomut * pnomut + 0.5 * pnomut * pmut
    elif parents == {2, 0}:
        # for AA or aa, must have one mutation and one without mutation; for Aa, either 2 or 0 mutations
        hered_prob["AA"] = pnomut * pmut
        hered_prob["Aa"] = pnomut * pnomut + pmut * pmut
        hered_prob["aa"] = pmut * pnomut
    else:
        # for {0, 0}, it is the reverse of {2, 2}
        hered_prob["AA"] = pmut * pmut
        hered_prob["Aa"] = 2 * pnomut * pmut
        hered_prob["aa"] = pnomut * pnomut

    if n_gene == 2:
        prob *= hered_prob["AA"]
    elif n_gene == 1:
        prob *= hered_prob["Aa"]
    else:
        prob *= hered_prob["aa"]

    return prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # update gene distribution
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        # update trait distribution
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        trait_sum = probabilities[person]["trait"][False] + probabilities[person]["trait"][True]
        gene_sum = probabilities[person]["gene"][0] + probabilities[person]["gene"][1] + probabilities[person]["gene"][2]
        probabilities[person]["trait"][False] /= trait_sum
        probabilities[person]["trait"][True] /= trait_sum
        probabilities[person]["gene"][0] /= gene_sum
        probabilities[person]["gene"][1] /= gene_sum
        probabilities[person]["gene"][2] /= gene_sum

if __name__ == "__main__":
    main()
