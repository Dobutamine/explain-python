from system_models.ductus_arteriosus import DuctusArteriosus


class Pda(DuctusArteriosus):
	"""Alias wrapper for the ductus arteriosus system model."""

	model_type = "pda"
