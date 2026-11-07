# Architecture and Product Direction

## Design goals

The platform is designed to separate data collection, modeling, settlement,
and evaluation. This makes it possible to test each layer independently and
prevents post-match data from changing the original prediction record.

## Production workflow

1. **Collect** current market snapshots from supported providers.
2. **Normalize** player, opponent, statistic, scope, line, and capture time.
3. **Resolve identities** against verified player identifiers.
4. **Cache history** at the player, series, and map levels.
5. **Project outcomes** using versioned assumptions and matchup context.
6. **Store immutable predictions** before the match begins.
7. **Settle conservatively** against completed match results.
8. **Export exceptions** rather than guessing when a match is ambiguous.
9. **Evaluate** error, bias, calibration, and decision accuracy.

## Why immutable snapshots matter

A projection must retain the line, inputs, model version, probability, and
timestamp that existed when the decision was made. Recomputing an old forecast
with newer data would introduce look-ahead bias and invalidate the evaluation.

## Why settlement is conservative

Player names, team aliases, substitutions, postponed matches, best-of-one
series, and missing maps can all cause incorrect automated results. The
production design settles only high-confidence matches and sends unresolved
records to a review queue.

## Evaluation layers

The research process distinguishes four questions:

1. **Accuracy:** How far are projections from actual results?
2. **Bias:** Does the model systematically project too high or too low?
3. **Calibration:** Do estimated probabilities match observed frequencies?
4. **Decision value:** Do actionable Over/Under signals beat the relevant
   payout threshold after pushes, prices, and market rules?

Good average accuracy does not guarantee profitable decisions. The production
roadmap therefore treats calibration and pricing as separate layers rather than
assuming every large model-to-line difference is expected value.

## Commercial roadmap

A paid application would add:

- Authenticated accounts and subscription entitlements
- Server-side collectors and scheduled refresh jobs
- Database-backed line history and model versioning
- User watchlists and configurable alerts
- Market-price and payout-aware expected-value calculations
- Monitoring for stale data and failed settlements
- Audit logs, responsible-use controls, and jurisdiction-aware availability

Those components are intentionally outside this public portfolio repository.
