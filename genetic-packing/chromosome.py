import math


class Chromosome:
    def __init__(self, number_of_boxes: int):
        self.number_of_boxes = number_of_boxes
        self.genes = []

    def get_bps(self):
        return [(index, score) for (index, score) in enumerate(self.genes[:self.number_of_boxes])]

    def get_vbo(self):
        return self.genes[self.number_of_boxes:]

    def __getitem__(self, item):
        return self.genes[item]

    def __len__(self):
        return self.number_of_boxes

    def append(self, gene):
        self.genes.append(gene)

    def decode_orientation(self, box_idx, orientations):
        gene = self.genes[self.number_of_boxes + box_idx]
        decoded_gene = math.ceil(gene * len(orientations))
        orientation = orientations[max(decoded_gene, 1) - 1]
        return orientation

    def set_genes(self, genes: []):
        self.genes = genes[:]


