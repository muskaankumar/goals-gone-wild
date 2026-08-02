# Model comparison

Headline outcome measures per model. The two designed contrast pairs (A:
safety-trained, B: capability) can be read off directly. The rightmost two
columns are the honesty-under-pressure result, conditioned on the model having
misaligned.

| model | n | misaligned | auth | truth | mean turns→viol. | conceal (given mis.) | full disc. (given mis.) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.5 | 256 | 36% | 36% | 0% | 81.1 | 1% | 14% |
| opus-4.8 | 216 | 62% | 62% | 0% | 32.4 | 3% | 86% |

_'conceal | misaligned' = share of that model's misaligned runs coded Non or
False at debrief; 'full disc. | misaligned' = share coded Full. Both are over
coded misaligned runs only._