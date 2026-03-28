# Chat Meal Logging - Visual Design Overview

## 🎨 UI Mockup

### Main Chat Window

```
┌─────────────────────────────────────────────────────────┐
│ 🍽️  Meal Logging Chat                            [×] [−] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 🤖 Hi! I'd love to help you log your meal.            │
│    What did you eat today?                            │
│                                                         │
│                              2:30 PM                   │
│                                                         │
│                                                         │
│ 👤 I had eggs with toast and butter                   │
│                              2:31 PM                   │
│                                                         │
│ 🤖 Great! How many eggs? And was it fried,           │
│    scrambled, or boiled? Also, how many slices         │
│    of bread?                                           │
│                              2:32 PM                   │
│                                                         │
│ 👤 2 scrambled eggs, 2 slices of wheat bread,         │
│    with butter and jam                                │
│                              2:33 PM                   │
│                                                         │
│ 🤖 Perfect! Let me organize this for you...           │
│                              2:33 PM                   │
│                                                         │
│ ┌───────────────────────────────────────────────────┐ │
│ │ 📋 Structured Meal Items                          │ │
│ ├───────────────────────────────────────────────────┤ │
│ │ Food Item        │ Quantity │ Unit                │ │
│ ├──────────────────┼──────────┼─────────────────────┤ │
│ │ Eggs, scrambled  │ 2        │ Pieces              │ │
│ │ Bread, wheat     │ 2        │ Slices              │ │
│ │ Butter           │ 1        │ Tablespoons (total) │ │
│ │ Jam              │ 1        │ Tablespoons (total) │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│ ┌──────────────────────┬──────────────────────────┐   │
│ │ [✓ Confirm]         │ [✎ Edit Items]          │   │
│ └──────────────────────┴──────────────────────────┘   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Type your response...          [📤 Send]               │
└─────────────────────────────────────────────────────────┘
```

### After Confirming Items

```
┌─────────────────────────────────────────────────────────┐
│ 🍽️  Meal Logging Chat                            [×] [−] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ [Previous conversation...]                            │
│                                                         │
│ 🤖 Great! Let me calculate the nutrition info...      │
│                              2:35 PM                   │
│                                                         │
│ ┌───────────────────────────────────────────────────┐ │
│ │ 📊 Nutrition Breakdown                            │ │
│ ├──────────────────────────────────────────────────┤ │
│ │ Food Item  │ Cals │ Protein │ Carbs │ Fat        │ │
│ ├────────────┼──────┼─────────┼───────┼────────────┤ │
│ │ Eggs (2)   │ 140  │ 12g     │ 1g    │ 11g        │ │
│ │ Bread (2)  │ 160  │ 8g      │ 28g   │ 2g         │ │
│ │ Butter     │ 102  │ 0.1g    │ 0g    │ 11.5g      │ │
│ │ Jam        │ 55   │ 0g      │ 14g   │ 0g         │ │
│ ├────────────┼──────┼─────────┼───────┼────────────┤ │
│ │ TOTAL      │ 457  │ 20.1g   │ 43g   │ 24.5g      │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│ 🤖 Your meal is ready! Would you like to save it?     │
│                              2:35 PM                   │
│                                                         │
│ ┌──────────────────────┬──────────────────────────┐   │
│ │ [✓ Save to Log]      │ [✎ Edit Items]          │   │
│ ├──────────────────────┼──────────────────────────┤   │
│ │ [🔄 Recalculate]                                │   │
│ └──────────────────────┴──────────────────────────┘   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Type your response...          [📤 Send]               │
└─────────────────────────────────────────────────────────┘
```

### Inline Edit Mode (when user clicks Edit)

```
┌─────────────────────────────────────────────────────────┐
│ 🍽️  Meal Logging Chat                            [×] [−] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌───────────────────────────────────────────────────┐ │
│ │ 📋 Edit Meal Items                                │ │
│ ├───────────────────────────────────────────────────┤ │
│ │ Food Item     │ Quantity │ Unit         │ Action  │ │
│ ├───────────────┼──────────┼──────────────┼─────────┤ │
│ │ Eggs, scram.. │ [2    ▼] │ [Pieces   ▼] │ [−]     │ │
│ │ Bread, wheat  │ [2    ▼] │ [Slices   ▼] │ [−]     │ │
│ │ Butter        │ [1    ▼] │ [Tbsp     ▼] │ [−]     │ │
│ │ Jam           │ [1    ▼] │ [Tbsp     ▼] │ [−]     │ │
│ │ [+ Add Item]                                      │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│ ┌──────────────────────┬──────────────────────────┐   │
│ │ [✓ Done Editing]     │ [✗ Cancel]              │   │
│ └──────────────────────┴──────────────────────────┘   │
│                                                         │
├─────────────────────────────────────────────────────────┤
```

---

## 🔄 Component Hierarchy

```
MealChatWindow (main component)
├── Header
│   ├── Title "Meal Logging Chat"
│   ├── Close button
│   └── Minimize button
│
├── ChatMessages (scrollable area)
│   ├── Message ({role: "assistant", content: "..."})
│   ├── Message ({role: "user", content: "..."})
│   ├── StructuredMealTable (inline)
│   │   ├── MealItemRow (editable on double-click)
│   │   ├── MealItemRow
│   │   └── [+ Add Row]
│   ├── NutritionTable (inline)
│   │   ├── NutritionRow
│   │   ├── NutritionRow
│   │   └── TotalRow (highlighted)
│   ├── ActionButtons
│   │   ├── [✓ Confirm]
│   │   ├── [✎ Edit Items]
│   │   ├── [✓ Save to Log]
│   │   └── [🔄 Recalculate]
│   └── Loading Spinner (while processing)
│
├── UserInputField
│   ├── TextInput (disabled while processing)
│   ├── Send Button
│   └── Character counter
│
└── Footer
    └── "Powered by AI" badge
```

---

## 📱 Responsive Design

### Desktop (1024px+)
```
┌──────────────────────────────────────────────┐
│  Chat Window (600px width)                   │
│  Centered, full height                       │
│  Tables with full width display              │
└──────────────────────────────────────────────┘
```

### Tablet (768px - 1023px)
```
┌─────────────────────────────────────────┐
│  Chat Window (500px width)              │
│  Tables slightly compressed             │
└─────────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌─────────────────────────────────────────┐
│  Chat Window (100% width, -20px padding)│
│  Tables collapse to stacked view        │
│  Buttons stack vertically               │
└─────────────────────────────────────────┘
```

---

## 🎭 User Interactions

### Interaction 1: Type & Send Message
```
User types in input field
        ↓
User clicks Send (or presses Enter)
        ↓
Input becomes disabled
        ↓
Loading spinner appears
        ↓
Bot responds with message
        ↓
Input becomes enabled
```

### Interaction 2: Confirm Items
```
User sees structured meal table
        ↓
User clicks [✓ Confirm] button
        ↓
Loading spinner appears
        ↓
Nutrition table appears
        ↓
Action buttons update to [✓ Save], [✎ Edit], etc.
```

### Interaction 3: Edit Items
```
User clicks [✎ Edit Items] button
        ↓
Table becomes editable
        ↓
Inline editing enabled (click cells to edit)
        ↓
User can add/remove rows
        ↓
User clicks [✓ Done Editing]
        ↓
Nutrition recalculates
```

### Interaction 4: Save Meal
```
User clicks [✓ Save to Log]
        ↓
Loading spinner appears
        ↓
Chat shows success message
        ↓
[Optional] Auto-redirect to meals page
```

---

## 🎨 Color & Styling

### Color Scheme (matches existing P.U.L.S.E palette)

```
Primary Colors:
- Primary: #3B82F6 (blue) - Buttons, highlights
- Success: #10B981 (green) - Confirm actions
- Danger: #EF4444 (red) - Delete/remove actions
- Warning: #F59E0B (amber) - Alerts

Background:
- Bot message: #F3F4F6 (light gray)
- User message: #DBEAFE (light blue)
- Tables: #FFFFFF (white)
- Borders: #E5E7EB (medium gray)

Text:
- Headings: #111827 (dark)
- Body: #374151 (medium)
- Secondary: #6B7280 (light)
```

### Component Styling

```
Buttons:
- [✓ Confirm]: Green (#10B981), large, full-width on mobile
- [✎ Edit]: Blue (#3B82F6), full-width on mobile
- [✓ Save]: Green, prominent
- [🔄 Recalculate]: Blue, secondary

Tables:
- Header: Bold, slightly darker background
- Rows: Alternating light/normal background
- Totals row: Highlighted, bold text
- Borders: Subtle, minimal

Chat Messages:
- Bot: Light gray background, left-aligned
- User: Light blue background, right-aligned
- Timestamps: Small, gray, right-aligned
```

---

## ⌨️ Keyboard Shortcuts (Optional)

```
Enter        - Send message
Shift+Enter  - New line in message
Escape       - Close chat (if not typing)
Ctrl+Z       - Undo last edit (in edit mode)
```

---

## 🔔 Toast Notifications

```
Success:
┌─────────────────────────────────────────┐
│ ✅ Meal saved successfully!             │
└─────────────────────────────────────────┘

Error:
┌─────────────────────────────────────────┐
│ ❌ Failed to find nutrition data        │
│    for "xyz". Please enter manually.    │
└─────────────────────────────────────────┘

Warning:
┌─────────────────────────────────────────┐
│ ⚠️  Session will expire in 5 minutes    │
└─────────────────────────────────────────┘
```

---

## 🎬 Animation & Transitions

```
Message Arrival:
- Fade in from bottom
- Duration: 300ms
- Easing: ease-in-out

Table Appearance:
- Slide up
- Duration: 400ms
- Easing: ease-out

Button Hover:
- Background color transition
- Duration: 200ms

Loading Spinner:
- Rotate animation
- Duration: 1s
- Infinite loop
```

---

## 📐 Spacing & Typography

```
Font Stack:
- Headers: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto
- Body: Same as headers
- Monospace: "Monaco", "Courier New"

Font Sizes:
- Header (h1): 24px, bold
- Message: 16px, regular
- Labels: 14px, semi-bold
- Small text (timestamps): 12px, light

Line Heights:
- Headers: 1.3
- Body: 1.5
- Compact: 1.4

Spacing:
- Padding (containers): 16px - 24px
- Margin (sections): 24px - 32px
- Gap (flex items): 8px - 16px
```

---

## ✨ Accessibility Features

```
- All buttons have aria-labels
- Color not used as only indicator (icons + text)
- Sufficient contrast ratio (WCAG AA)
- Focus indicators visible on all interactive elements
- Keyboard navigation support
- Screen reader friendly message structure
- Loading states announced via aria-live
```

---

## 🚀 Performance Considerations

```
- Lazy load chat window (modal)
- Virtualize long message lists (500+ messages)
- Memoize table components
- Debounce table edits before sending
- Cache nutrition data
- Minimize re-renders with React.memo
```

---

**This visual design completes the comprehensive design package!**

All components are ready for frontend implementation using React + TypeScript + Tailwind CSS.
