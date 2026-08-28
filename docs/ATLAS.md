# Atlas Map

The atlas is a Codex v2 sprite sheet with 8 columns, 11 rows, and `192x208` cells.

| Row | State | Frames | Meaning |
| ---: | --- | ---: | --- |
| 0 | `idle` | 6 | Breathing and blinking |
| 1 | `running-right` | 8 | Drag movement toward screen-right |
| 2 | `running-left` | 8 | Drag movement toward screen-left |
| 3 | `waving` | 4 | Greeting gesture |
| 4 | `jumping` | 5 | Vertical jump loop |
| 5 | `failed` | 8 | Blocked or failed reaction |
| 6 | `waiting` | 6 | Waiting for approval or input |
| 7 | `running` | 6 | Active task processing |
| 8 | `review` | 6 | Focused output review |
| 9 | look directions | 8 | `000`, `022.5`, `045`, `067.5`, `090`, `112.5`, `135`, `157.5` |
| 10 | look directions | 8 | `180`, `202.5`, `225`, `247.5`, `270`, `292.5`, `315`, `337.5` |

Direction semantics are clockwise: `000` is up, `090` is screen-right, `180` is down, and `270` is screen-left. Neutral/front falls back to the idle row.
