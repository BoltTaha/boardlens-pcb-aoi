# Troubleshooting

## `/ready` reports degraded

No model marked `ready` is installed. Fit and validate a product model, place the artifact at the configured location, update its metadata/status, and restart the service. Do not bypass this with a placeholder file.

## PatchCore fit runs out of memory

Reduce batch size first, then input resolution or the number of normal fitting images in a documented experiment. A smaller coreset reduces the final bank but does not remove the peak cost of collecting full embeddings. Avoid comparing changed configurations as though they were the same benchmark.

## First fit tries to access the network

The ImageNet backbone weights are downloaded on first use. Run once in an authorized network environment and retain the trusted cache/artifact metadata. Do not silently set `pre_trained=False`; that changes the method materially.

## Migration says the table already exists

An older development database may have been created by SQLAlchemy before Alembic was introduced. Verify its schema, back it up, then use `alembic stamp head` only if it genuinely matches revision 0001. Fresh databases should use `alembic upgrade head`.

## Inspection returns REVIEW with no score

This is expected fail-safe behavior when the product model is absent or unloadable. Inspect `/models`, `/ready`, and the configured artifact path.

