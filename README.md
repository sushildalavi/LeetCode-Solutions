# LeetCode Solutions and Interview Prep

This repository is my long-term DSA and interview prep workspace. Accepted solutions are synced from LeetCode through `LeetSync`, and the tracked sheet progress in this README is refreshed automatically from the synced problem folders and files.

## Profiles

[🚀](https://neetcode.io/profile) NeetCode Profile  
[<img src="https://cdn.simpleicons.org/leetcode/FFA116" alt="LeetCode" width="18" />](https://leetcode.com/u/Sush2411/) LeetCode Profile

## Prep Roadmap

1. Finish `NeetCode 150`
2. Move to `NeetCode 250`
3. Complete `Striver's SDE Sheet`
4. Continue with regular DSA practice for revision, speed, and pattern recognition

## Progress

<!-- progress:begin -->
| Track | Solved | Total | Progress |
| --- | ---: | ---: | ---: |
| NeetCode 150 | 0 | 150 | 0.0% |
| NeetCode 250 | 0 | 250 | 0.0% |
| Striver's SDE Sheet (LeetCode-backed) | 0 | 117 | 0.0% |

Tracked unique problems solved across all sheets: `0 / 293`
<!-- progress:end -->

## How This Repo Updates

- Solve on `LeetCode`
- Let `LeetSync` push the accepted submission into this repository
- The GitHub Action scans the synced solution names and refreshes the progress table in this README
- The same workflow creates or updates per-problem notes in [`notes/problems/`](notes/problems), syncs the problem statement, and refreshes the index at [`notes/INDEX.md`](notes/INDEX.md)
- If the repo has an `OPENAI_API_KEY` secret, the workflow also generates a draft summary, data structures list, approach, and complexity directly from your synced accepted solution

## Knowledge Capture

- Your solution code is saved by `LeetSync`
- A note file is generated automatically for each synced problem with:
  - LeetCode link
  - difficulty
  - topic tags
  - synced problem statement
  - tracked sheet membership
  - synced solution paths
- If `OPENAI_API_KEY` is configured as a GitHub Actions secret, the note also gets an auto-generated draft for:
  - problem summary
  - data structures used
  - approach
  - time/space complexity
- You can still edit the generated note manually afterward; existing non-`TODO` sections are preserved

To save your own approach quickly after solving, use:

```bash
python3 scripts/update_problem_note.py two-sum \
  --summary "Find two indices whose values add up to the target." \
  --data-structures "Array, Hash Map" \
  --approach "Use a one-pass hash map to store seen values and check complements." \
  --time "O(n)" \
  --space "O(n)"
```

## Notes

- `NeetCode 150` is a subset of `NeetCode 250`, so those counts intentionally overlap
- `Striver's SDE Sheet` tracking only covers the LeetCode-backed problems from the official sheet
- If a Striver problem is not solved on LeetCode, `LeetSync` cannot sync it into this repository
- For full note automation, add `OPENAI_API_KEY` as a repository secret in GitHub Actions
