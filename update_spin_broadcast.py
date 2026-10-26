path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = """          playPlayroomSynthesizer('!gacha', 0.8);

          showToast(`🎡 ผลสุ่มวงล้อ: ${chosen}`);

        }

      }, 90);"""

replacement = """          playPlayroomSynthesizer('!gacha', 0.8);

          showToast(`🎡 ผลสุ่มวงล้อ: ${chosen}`);

          // Broadcast to Canvas and OBS Overlay
          const spinPayload = {
            items: lines,
            winner: chosen,
            duration: 6
          };
          if (window.BP3_BUS) {
            window.BP3_BUS.emit('RANDOMIZER_SPIN', spinPayload);
          }
          if ('BroadcastChannel' in window) {
            try {
              const bus = new BroadcastChannel('bp3_system_channel');
              bus.postMessage({
                event: 'RANDOMIZER_SPIN',
                payload: spinPayload
              });
            } catch (e) {}
          }

        }

      }, 90);"""

if target in c:
    c = c.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Successfully updated runSpinRandomizer to broadcast RANDOMIZER_SPIN!")
else:
    print("Warning: target not found!")
