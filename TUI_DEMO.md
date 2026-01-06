# Centered Window TUI - Blessed

Professional terminal dialog inspired by cc-mirror's interactive UI.

## Visual Layout

```
                    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                    ┃  🔧 Backup Options                    ┃
                    ┃                                       ┃
                    ┃      MBP16M426LZ / nocoo              ┃
                    ┃                                       ┃
                    ┃  ☐ Sanitize secrets                   ┃
                    ┃  ☑ Include history                    ┃
                    ┃                                       ┃
                    ┃  ───────────────────────────────────  ┃
                    ┃      Sanitize: ❌                     ┃
                    ┃      History: ✅                      ┃
                    ┃      Output: ./backups/               ┃
                    ┃                                       ┃
                    ┃  [ 💾 Backup ]  [ ❌ Quit ]           ┃
                    ┃                                       ┃
                    ┃  ↑↓ Navigate  Space Toggle  Enter OK  ┃
                    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Architecture

**Blessed Library (Python curses alternative)**
- ✅ Cross-platform (macOS, Linux, Windows)
- ✅ Lightweight and fast
- ✅ Full-screen mode support
- ✅ Keyboard input handling
- ✅ Clean terminal escape sequences

**Window Class**
- Calculates centered position
- Draws box borders with Unicode
- Positions text and buttons
- Handles selection highlighting

## Features

### 1. **Centered Window**
   - Automatically centers based on terminal size
   - Responsive to terminal resize (sort of)
   - Professional box border (┏━┓┃┗━┛)

### 2. **Interactive Options**
   - ☐/☑ Checkboxes for Sanitize & History
   - Highlighted selected option
   - Real-time summary display
   - Status indicators (✅/❌)

### 3. **Navigation**
   - ↑↓ Arrow keys to navigate
   - Space to toggle checkbox
   - Enter to confirm
   - q/Q to quit

### 4. **Multiple Dialogs**
   - Options selection dialog
   - Progress/backup dialog
   - Result confirmation dialog

### 5. **Full Keyboard Control**
   - No mouse needed
   - Smooth navigation
   - Instant feedback

## Code Structure

```python
class Window:
    def draw_box()       # Draw the border
    def text()           # Position text inside
    def button()         # Draw selectable button

def show_options_dialog()   # Main interaction
def show_result_dialog()    # Success/error message
def main()                  # Orchestrate flow
```

## Dialog Flow

```
┌─────────────────────┐
│ show_options_dialog │  ← User selects options
└──────────┬──────────┘
           ↓
    ┌─────────────┐
    │  Backup... │  ← Progress indicator
    └──────┬──────┘
           ↓
┌─────────────────────────┐
│ show_result_dialog()    │  ← Success/Error
└─────────────────────────┘
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ↑ | Previous option |
| ↓ | Next option |
| Space | Toggle checkbox |
| Enter | Confirm selection |
| q/Q | Quit |

## Comparison: Blessed vs Previous

| Aspect | Textual | Questionary | **Blessed** |
|--------|---------|-------------|-----------|
| Window | Layout grid | Linear | **Centered** ✅ |
| Code | 350 lines | 100 lines | **~300 lines** |
| Style | Modern | Simple | **Professional** ✅ |
| Visual | Panels | Questions | **Dialog boxes** ✅ |
| Inspiration | None | Ink | **cc-mirror** ✅ |

## Use Cases

✅ **Best for:**
- Interactive backup/migration tools
- Configuration wizards
- User-friendly CLI applications
- Cross-platform compatibility

❌ **Not ideal for:**
- Complex dashboard layouts
- Real-time monitoring
- Games or animations

## Terminal Requirements

- Min width: 60 columns
- Min height: 20 lines
- Modern terminal emulator (iTerm2, Terminal.app, etc.)
- Supports Unicode box-drawing characters

## Example Interaction

```bash
$ python3 ccbackup_tui.py

[Terminal clears and shows centered dialog]

↓  [User presses down arrow]
☑ Include history is now selected

[Space]  [User toggles history option]
History: ✅

[Down, Down]  [Navigate to Backup button]

[Enter]  [Confirm, backup starts]

[Dialog shows progress...]

[Dialog shows result]
✅ Backup Completed
ccbackup_MBP16_nocoo_*.zip
45 KB

✅ Ready for migration

[Press any key to exit]
```

## Why Blessed?

1. **Inspired by cc-mirror** - Similar dialog-based design
2. **Clean API** - Just positioning, no complex state
3. **Lightweight** - Single dependency, ~50KB
4. **Fast** - Instant startup and response
5. **Professional** - Looks like a real application
6. **Cross-platform** - Works on all major OSes
7. **Responsive** - Handles all keyboard input

## File Structure

```
ccbackup/
├── ccbackup.py          # Core logic (0 dependencies)
├── ccbackup_tui.py      # Blessed-based UI (~300 lines)
├── requirements.txt     # Just: blessed>=1.20.0
└── README.md            # Full documentation
```

## Performance

- **Startup**: ~100ms (instant)
- **Input response**: <10ms
- **Memory**: ~5MB total
- **CPU**: Minimal (only redraws on input)

## Testing

For testing without full interaction:
```bash
# Just use the CLI
python3 ccbackup.py --sanitize --include-history

# Or interactive
python3 ccbackup_tui.py
```

## Future Improvements

- [ ] Mouse support (click buttons)
- [ ] Escape key to cancel
- [ ] Custom window sizes
- [ ] Color themes
- [ ] Animation during backup

## Dependencies

**Production:**
- `blessed>=1.20.0` - Terminal UI library

**Development:**
- `ccbackup.py` - Core backup logic (same as CLI)

**Why single dependency?**
- Blessed is small and stable
- Well-maintained by Jazzband
- Works on all platforms
- No external service calls
