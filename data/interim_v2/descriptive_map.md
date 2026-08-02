# Descriptive behavior map

Distribution of behaviors when the agent is blocked (multi-label; a run can
carry several tags).

## Overall

| behavior | runs | share |
| --- | --- | --- |
| stopped | 144 | 50% |
| retried_with_fix | 0 | 0% |
| tried_different_approach | 0 | 0% |
| asked_for_help_in_channel | 0 | 0% |
| crossed_boundary | 144 | 50% |
| redefined_success | 0 | 0% |
| claimed_false_success | 72 | 25% |

## By finality

| finality | n | stopped | retried_with_fix | tried_different_approach | asked_for_help_in_channel | crossed_boundary | redefined_success | claimed_false_success |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| final_this_attempt | 96 | 48 (50%) | 0 (0%) | 0 (0%) | 0 (0%) | 48 (50%) | 0 (0%) | 24 (25%) |
| never_reconsidered | 96 | 48 (50%) | 0 (0%) | 0 (0%) | 0 (0%) | 48 (50%) | 0 (0%) | 24 (25%) |
| retry_invited | 96 | 48 (50%) | 0 (0%) | 0 (0%) | 0 (0%) | 48 (50%) | 0 (0%) | 24 (25%) |