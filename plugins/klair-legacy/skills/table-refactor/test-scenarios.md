# Table Refactor Skill - Test Scenarios

This document outlines test scenarios for validating the table refactor skill. Use these scenarios to ensure the skill handles different table migration cases effectively.

## Scenario Categories

1. [Simple Tables](#simple-tables)
2. [Hierarchical Tables](#hierarchical-tables)
3. [Tables with Comments](#tables-with-comments)
4. [Financial Tables](#financial-tables)
5. [Custom Feature Tables](#custom-feature-tables)
6. [Backend Integration](#backend-integration)
7. [Edge Cases](#edge-cases)

---

## Simple Tables

### Scenario 1.1: Basic Table with Sorting and Pagination

**Input:**
- A simple HTML table with manual sorting implementation
- Client-side data array
- No pagination (shows all rows)

**Expected Output:**
- UnifiedTable with TABLE_PRESETS.BASIC
- Columns with appropriate formatTypes
- Pagination enabled with default pageSize
- Sorting enabled on all columns

**Success Criteria:**
- [ ] Data displays correctly
- [ ] Sorting works on all columns
- [ ] Pagination controls appear and function
- [ ] No console errors

### Scenario 1.2: Material-UI DataGrid Migration

**Input:**
- Table using MUI DataGrid
- Custom column definitions
- Built-in filtering and search

**Expected Output:**
- UnifiedTable with equivalent features
- Column definitions mapped to ColumnDef format
- Search functionality preserved

**Success Criteria:**
- [ ] All columns render correctly
- [ ] Search works on designated columns
- [ ] Performance is equal or better
- [ ] Styling matches application theme

### Scenario 1.3: Custom Table with Row Selection

**Input:**
- Custom table with checkbox selection
- Selected rows tracked in state
- Actions based on selection

**Expected Output:**
- UnifiedTable with custom column for selection
- State management preserved
- Actions integrated via customHeaderControls

**Success Criteria:**
- [ ] Row selection works
- [ ] Bulk actions work correctly
- [ ] Selection state persists across pagination
- [ ] Visual feedback for selected rows

---

## Hierarchical Tables

### Scenario 2.1: Two-Level Accordion Table

**Input:**
- Parent-child relationship (e.g., Categories → Products)
- Expandable/collapsible rows
- Summary data at parent level

**Expected Output:**
- UnifiedTable with hierarchical data structure
- TABLE_PRESETS.ACCORDION
- Proper level and expandable properties

**Success Criteria:**
- [ ] Parent rows are expandable
- [ ] Child rows display when expanded
- [ ] Summary data shows correctly
- [ ] Expand/collapse icons appear
- [ ] Indentation indicates hierarchy

### Scenario 2.2: Multi-Level Corporate Hierarchy

**Input:**
- 3+ levels (e.g., Company → Department → Team → Employee)
- Different data at each level
- Aggregated totals at parent levels

**Expected Output:**
- UnifiedTable with TABLE_PRESETS.CORPORATE
- Recursive data structure with children
- TotalRow configuration for aggregations

**Success Criteria:**
- [ ] All levels render correctly
- [ ] Navigation through levels works
- [ ] Totals aggregate properly
- [ ] Performance with deep nesting is acceptable

### Scenario 2.3: Product Catalog with Variants

**Input:**
- Products with multiple variants
- Variant-specific pricing and inventory
- Category-level organization

**Expected Output:**
- UnifiedTable with TABLE_PRESETS.CATALOG
- Three-level structure (Category → Product → Variant)
- Currency formatting for prices

**Success Criteria:**
- [ ] Category, product, and variant levels distinct
- [ ] Prices format as currency
- [ ] Inventory numbers format correctly
- [ ] Search works across all levels

---

## Tables with Comments

### Scenario 3.1: Simple Table with Cell Comments

**Input:**
- Flat table with commenting on specific cells
- Existing comment API integration

**Expected Output:**
- UnifiedTableWithCommentsWrapper
- TABLE_PRESETS.COMMENTS
- Comment handlers implemented

**Success Criteria:**
- [ ] Comments can be created on cells
- [ ] Comment indicators appear
- [ ] Comment threads work correctly
- [ ] Mention system functions
- [ ] Comments persist after page reload

### Scenario 3.2: Hierarchical Table with Comments

**Input:**
- Multi-level table with comments on any level
- Path-based comment identification

**Expected Output:**
- UnifiedTableWithCommentsWrapper with hierarchical data
- Proper commentsIdField configuration
- Path-based element IDs

**Success Criteria:**
- [ ] Comments work on parent rows
- [ ] Comments work on child rows
- [ ] Element IDs are unique across hierarchy
- [ ] Comment highlighting works correctly
- [ ] Thread deletion works at all levels

### Scenario 3.3: Financial Report with Comments

**Input:**
- Financial table with line-item comments
- Comment threads on specific accounts
- User mentions and notifications

**Expected Output:**
- UnifiedTableWithCommentsWrapper
- TABLE_PRESETS.FINANCIAL features + comments
- Total rows with comment support

**Success Criteria:**
- [ ] Financial formatting preserved
- [ ] Comments work on financial line items
- [ ] Total rows display correctly
- [ ] Export includes comments metadata

---

## Financial Tables

### Scenario 4.1: Income Statement

**Input:**
- Revenue, expenses, and net income
- Multiple columns (Actual, Budget, Variance)
- Calculated totals and subtotals

**Expected Output:**
- UnifiedTable with TABLE_PRESETS.FINANCIAL
- Multiple total rows (subtotals and grand total)
- Currency and percentage formatting

**Success Criteria:**
- [ ] All financial data formats correctly
- [ ] Totals calculate accurately
- [ ] Variance calculations show correctly
- [ ] Export to Excel works
- [ ] Negative values display appropriately

### Scenario 4.2: Balance Sheet with Hierarchy

**Input:**
- Assets, Liabilities, Equity sections
- Sub-categories within each section
- Calculated section totals

**Expected Output:**
- UnifiedTable with hierarchical structure
- TotalRow for each section
- Currency formatting throughout

**Success Criteria:**
- [ ] Hierarchy reflects accounting structure
- [ ] Section totals calculate correctly
- [ ] Assets = Liabilities + Equity validates
- [ ] Drill-down to account level works

### Scenario 4.3: Budget vs Actuals Analysis

**Input:**
- Monthly budget and actual data
- Variance analysis columns
- Year-to-date calculations

**Expected Output:**
- UnifiedTable with TABLE_PRESETS.FINANCIAL
- Custom variance calculation columns
- Conditional formatting for positive/negative variance

**Success Criteria:**
- [ ] Budget and actuals display side-by-side
- [ ] Variance calculates correctly
- [ ] Percentage variance formats correctly
- [ ] Colors indicate favorable/unfavorable variance
- [ ] YTD totals calculate correctly

---

## Custom Feature Tables

### Scenario 5.1: Table with Custom Filters

**Input:**
- Table with multiple dropdown filters
- Date range picker
- Complex filter logic (AND/OR conditions)

**Expected Output:**
- UnifiedTable with customHeaderControls
- Filter state managed in parent component
- Filtered data passed to UnifiedTable

**Success Criteria:**
- [ ] All filters render in header
- [ ] Filters apply correctly
- [ ] Multiple filters work together
- [ ] Filter state persists
- [ ] Clear filters option works

### Scenario 5.2: Table with Inline Editing

**Input:**
- Table with editable cells
- Save/cancel functionality
- Validation on edit

**Expected Output:**
- UnifiedTable with custom render functions
- Edit mode state management
- Validation feedback

**Success Criteria:**
- [ ] Cells become editable on click
- [ ] Validation prevents invalid input
- [ ] Changes save correctly
- [ ] Cancel reverts changes
- [ ] Loading state during save

### Scenario 5.3: Table with Drag-and-Drop Reordering

**Input:**
- Table with draggable rows
- Reorder persistence
- Visual feedback during drag

**Expected Output:**
- UnifiedTable with custom row wrapper
- Drag-and-drop library integration
- Reorder API integration

**Success Criteria:**
- [ ] Rows are draggable
- [ ] Visual feedback during drag
- [ ] Drop zones indicated clearly
- [ ] Order persists after reorder
- [ ] Pagination doesn't break reordering

---

## Backend Integration

### Scenario 6.1: Server-Side Pagination

**Input:**
- Large dataset (10,000+ rows)
- Backend supports pagination parameters
- API returns page metadata

**Expected Output:**
- UnifiedTable with server-side pagination
- API service updated for pagination params
- Loading state during fetch

**Success Criteria:**
- [ ] Only current page data fetched
- [ ] Page navigation triggers API calls
- [ ] Total page count displays correctly
- [ ] Loading indicator shows during fetch
- [ ] Performance is fast (< 1s per page)

### Scenario 6.2: Backend Data Structure Mismatch

**Input:**
- Backend returns nested JSON
- Field names don't match frontend expectations
- Data types need conversion

**Expected Output:**
- Data adapter function created
- Field mapping documented
- Type conversions handled

**Success Criteria:**
- [ ] Adapter transforms data correctly
- [ ] All fields map properly
- [ ] Type conversions work (string to number, etc.)
- [ ] No data loss in transformation
- [ ] Performance impact minimal

### Scenario 6.3: Backend API Enhancement

**Input:**
- Backend doesn't support sorting/filtering
- New endpoint needed for UnifiedTable features

**Expected Output:**
- New backend endpoint created
- Sorting and filtering parameters added
- Backend adapter maintains backward compatibility

**Success Criteria:**
- [ ] New endpoint works correctly
- [ ] Old endpoint still functional (if needed)
- [ ] Sorting parameter respected
- [ ] Filtering parameter respected
- [ ] API documentation updated

---

## Edge Cases

### Scenario 7.1: Empty Data

**Input:**
- API returns empty array
- No data available message needed

**Expected Output:**
- UnifiedTable shows empty state
- Graceful "No data" message
- No console errors

**Success Criteria:**
- [ ] Empty state displays
- [ ] Message is user-friendly
- [ ] No crashes or errors
- [ ] Pagination hides or shows "0 of 0"

### Scenario 7.2: Very Long Text in Cells

**Input:**
- Data with very long strings (1000+ characters)
- No truncation in original table

**Expected Output:**
- UnifiedTable with proper text overflow handling
- Tooltip on hover or expand option

**Success Criteria:**
- [ ] Long text doesn't break layout
- [ ] Text is readable (wrapped or truncated)
- [ ] Tooltip shows full text if truncated
- [ ] Performance not affected

### Scenario 7.3: Null and Undefined Values

**Input:**
- Data with null, undefined, and empty string values
- No explicit null handling in original table

**Expected Output:**
- UnifiedTable with proper null handling
- Default values or empty display

**Success Criteria:**
- [ ] Null values don't cause errors
- [ ] Undefined values don't cause errors
- [ ] Empty strings display appropriately
- [ ] Sorting handles nulls correctly
- [ ] Filtering handles nulls correctly

### Scenario 7.4: Special Characters and HTML

**Input:**
- Data with special characters (&, <, >, quotes)
- HTML entities in strings

**Expected Output:**
- UnifiedTable with proper escaping
- HTML rendered safely or as text

**Success Criteria:**
- [ ] Special characters display correctly
- [ ] No XSS vulnerabilities
- [ ] HTML entities decode properly
- [ ] Search works with special characters

### Scenario 7.5: Performance with Large Dataset (Client-Side)

**Input:**
- Dataset with 1000+ rows
- All loaded client-side
- Complex calculated columns

**Expected Output:**
- UnifiedTable with pagination
- Memoized calculations
- Virtual scrolling or pagination to limit render

**Success Criteria:**
- [ ] Initial render < 2 seconds
- [ ] Sorting < 500ms
- [ ] Pagination instant
- [ ] No frame drops during interaction
- [ ] Memory usage reasonable

---

## Testing Checklist

For each scenario, verify:

### Functional Tests
- [ ] All features from original table work
- [ ] New features (if any) work correctly
- [ ] Data displays accurately
- [ ] User interactions respond correctly

### Visual Tests
- [ ] Layout matches design
- [ ] Responsive on mobile/tablet
- [ ] Dark mode (if applicable)
- [ ] Hover/focus states work
- [ ] Accessibility (keyboard navigation)

### Performance Tests
- [ ] Initial load time acceptable
- [ ] Interaction responsiveness good
- [ ] Memory usage reasonable
- [ ] No memory leaks

### Code Quality
- [ ] TypeScript types correct
- [ ] No console warnings/errors
- [ ] Code follows project standards
- [ ] Comments explain complex logic
- [ ] No unused code

### Documentation
- [ ] Component usage documented
- [ ] Data adapter documented
- [ ] API changes documented (if any)
- [ ] Migration notes added

---

## Reporting Issues

If a scenario fails, document:
1. **Scenario ID** (e.g., 1.1, 2.2)
2. **What happened** (actual behavior)
3. **What should happen** (expected behavior)
4. **Steps to reproduce**
5. **Screenshots/videos** (if applicable)
6. **Skill suggestions** (what the skill told you to do)
7. **Environment** (browser, OS, versions)

Use this information to improve the skill and refactoring process.

---

## Success Metrics

A successful table refactoring should achieve:

1. **Feature Parity**: 100% of original features work
2. **Performance**: Equal or better than original
3. **Code Reduction**: Less code overall (DRY principle)
4. **Maintainability**: Easier to update and modify
5. **Consistency**: Matches other refactored tables
6. **User Experience**: Equal or improved UX
7. **Accessibility**: Better or equal a11y
8. **Test Coverage**: Adequate testing in place

---

*Use these scenarios to validate the table refactor skill and ensure comprehensive coverage of refactoring cases.*
