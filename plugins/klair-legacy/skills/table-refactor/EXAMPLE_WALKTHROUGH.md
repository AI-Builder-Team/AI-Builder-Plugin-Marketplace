# Table Refactor Skill - Example Walkthrough

This document provides a complete example of using the table refactor skill to migrate a custom table to UnifiedTable.

## Example: Refactoring a Customer List Table

### Original Component

Let's say we have a custom customer table component:

```typescript
// klair-client/src/components/CustomerTable.tsx
import React, { useState, useEffect } from 'react';
import { fetchCustomers } from '@/services/customerService';

interface Customer {
  id: string;
  name: string;
  email: string;
  revenue: number;
  status: 'active' | 'inactive';
  joinDate: string;
}

const CustomerTable: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [sortField, setSortField] = useState<keyof Customer>('name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    setLoading(true);
    const data = await fetchCustomers();
    setCustomers(data);
    setLoading(false);
  };

  const handleSort = (field: keyof Customer) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedCustomers = [...filteredCustomers].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    const modifier = sortDirection === 'asc' ? 1 : -1;
    return aVal > bVal ? modifier : -modifier;
  });

  if (loading) return <div>Loading...</div>;

  return (
    <div className="customer-table">
      <div className="table-header">
        <h2>Customers</h2>
        <input
          type="text"
          placeholder="Search customers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      <table>
        <thead>
          <tr>
            <th onClick={() => handleSort('name')}>Name</th>
            <th onClick={() => handleSort('email')}>Email</th>
            <th onClick={() => handleSort('revenue')}>Revenue</th>
            <th onClick={() => handleSort('status')}>Status</th>
            <th onClick={() => handleSort('joinDate')}>Join Date</th>
          </tr>
        </thead>
        <tbody>
          {sortedCustomers.map(customer => (
            <tr key={customer.id}>
              <td>{customer.name}</td>
              <td>{customer.email}</td>
              <td>${customer.revenue.toLocaleString()}</td>
              <td>
                <span className={`badge ${customer.status}`}>
                  {customer.status}
                </span>
              </td>
              <td>{new Date(customer.joinDate).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CustomerTable;
```

### Step-by-Step Refactoring

#### Phase 1: Analysis

**User invokes skill:**
```
Use the table-refactor skill to refactor CustomerTable.tsx
```

**Skill Response:**
```
I'll help you refactor the CustomerTable component to use UnifiedTable. Let me start by analyzing the current implementation.

Reading: klair-client/src/components/CustomerTable.tsx
Reading: klair-client/src/components/tables/UnifiedTable/USAGE.md

Analysis Complete:
✓ Table Type: Simple (flat data structure)
✓ Data Source: API via fetchCustomers()
✓ Features Identified:
  - Sorting (all columns)
  - Search (name, email)
  - Loading state
  - Custom status badge rendering
✓ Columns: 5 (name, email, revenue, status, joinDate)
✓ Backend: Existing API at customerService

Recommendation:
- Use UnifiedTable with TABLE_PRESETS.BASIC
- Create custom render for status badge
- Add currency formatting for revenue
- Add date formatting for joinDate
- No data adapter needed (data structure is compatible)
```

#### Phase 2: Planning

**Skill provides plan:**
```
Refactoring Plan:
1. Define columns with appropriate formatTypes
2. Use TABLE_PRESETS.BASIC (includes sort, search, pagination)
3. Create custom renderer for status badge
4. Format revenue as currency
5. Keep existing data fetching logic
6. Remove manual sort/search logic (UnifiedTable handles this)

Proceeding with implementation...
```

#### Phase 3: Implementation

**Skill creates the refactored component:**

```typescript
// klair-client/src/components/CustomerTable.tsx (REFACTORED)
import React, { useState, useEffect, useMemo } from 'react';
import { UnifiedTable, TABLE_PRESETS, ColumnDef } from '@/components/tables/UnifiedTable';
import { fetchCustomers } from '@/services/customerService';

interface Customer {
  id: string;
  name: string;
  email: string;
  revenue: number;
  status: 'active' | 'inactive';
  joinDate: string;
}

const CustomerTable: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    setLoading(true);
    const data = await fetchCustomers();
    setCustomers(data);
    setLoading(false);
  };

  // Define columns with formatting and custom renderers
  const columns: ColumnDef<Customer>[] = useMemo(() => [
    {
      key: 'name',
      header: 'Customer Name',
      sticky: true,
      tooltip: 'Customer full name'
    },
    {
      key: 'email',
      header: 'Email Address',
      tooltip: 'Primary contact email'
    },
    {
      key: 'revenue',
      header: 'Total Revenue',
      formatType: 'currency',
      currencySymbol: '$',
      decimalPlaces: 2,
      align: 'right',
      tooltip: 'Total lifetime revenue from customer'
    },
    {
      key: 'status',
      header: 'Status',
      align: 'center',
      render: (value: string) => (
        <span className={`badge ${value === 'active' ? 'badge-success' : 'badge-warning'}`}>
          {value}
        </span>
      ),
      tooltip: 'Current account status'
    },
    {
      key: 'joinDate',
      header: 'Join Date',
      render: (value: string) => new Date(value).toLocaleDateString(),
      tooltip: 'Date customer joined'
    }
  ], []);

  // Prepare data in UnifiedTable format
  const tableData = useMemo(() => ({
    data: customers
  }), [customers]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="spinner">Loading customers...</div>
      </div>
    );
  }

  return (
    <UnifiedTable<Customer>
      data={tableData}
      columns={columns}
      features={{
        ...TABLE_PRESETS.BASIC,
        export: true,
        totalRow: true
      }}
      title="Customers"
      description="Manage and view all customer information"
      searchableColumns={['name', 'email']}
      pageSize={25}
      initialSort={{
        key: 'name',
        direction: 'ascending'
      }}
      totalRowConfig={{
        position: 'bottom',
        calculate: true,
        label: 'Total',
        excludeColumns: ['name', 'email', 'status', 'joinDate']
      }}
    />
  );
};

export default CustomerTable;
```

**Skill explains changes:**
```
Changes Made:
✅ Removed manual sorting logic (UnifiedTable handles this)
✅ Removed manual search logic (UnifiedTable handles this)
✅ Removed manual state for sortField, sortDirection, searchTerm
✅ Added column definitions with proper typing
✅ Added currency formatting for revenue
✅ Added date formatting for joinDate
✅ Preserved custom status badge rendering
✅ Added sticky first column
✅ Added tooltips for better UX
✅ Added export functionality (bonus feature)
✅ Added total row for revenue (bonus feature)
✅ Used useMemo for performance optimization

Code reduction: ~60 lines → ~70 lines (but gained features!)
Complexity reduction: Eliminated manual sort/search logic
```

#### Phase 4: Backend Integration

**Skill checks backend:**
```
Checking backend API...

API Endpoint: fetchCustomers() in customerService.ts
Response Format: Array<Customer>
✓ Data structure is compatible (no adapter needed)
✓ All required fields present
✓ Field types match expectations

No backend changes required.
```

#### Phase 5: Testing

**Skill provides testing guidance:**
```
Testing Checklist:

Functional Tests:
□ Data loads correctly
□ All 5 columns display
□ Sorting works on all columns
□ Search works (try searching by name and email)
□ Pagination appears (if > 25 customers)
□ Status badge displays with correct colors
□ Revenue displays as currency (e.g., $1,234.56)
□ Join date displays in locale format
□ Export button works
□ Total row shows sum of revenue

Visual Tests:
□ Layout matches application theme
□ Sticky name column works on scroll
□ Responsive on mobile
□ Dark mode works (if enabled)
□ Status badges styled correctly
□ Tooltips appear on column headers

Edge Cases:
□ Empty customer list shows appropriate message
□ Single customer displays correctly
□ Very long names don't break layout
□ Null/undefined revenue handled gracefully

Please test these scenarios and let me know if any issues arise.
```

**User tests and reports:**
```
All tests pass! The refactored table works great. The export feature is a nice bonus.
```

#### Phase 6: Cleanup

**Skill finalizes:**
```
Excellent! Let's complete the refactoring.

Cleanup Tasks:
✓ No old component to remove (we refactored in place)
✓ Verified no unused imports
✓ Added JSDoc comments for clarity
✓ TypeScript types are correct
✓ No console warnings

Code Review Checklist:
☑ TypeScript types properly defined
☑ No console warnings or errors
☑ Follows project coding standards
☑ Comments explain custom logic
☑ No unused code or imports
☑ All features tested and working
☑ Performance is good
☑ Accessibility maintained

Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ CustomerTable successfully refactored to UnifiedTable
✅ All original features preserved
✅ Added export functionality
✅ Added total row calculation
✅ Reduced code complexity
✅ Improved maintainability
✅ Better user experience
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The refactored component is ready for code review and merge!
```

---

## Key Takeaways from This Example

### What Worked Well
1. **Skill automatically identified** the table type and features
2. **No data adapter needed** because structure was compatible
3. **Simplified code** by removing manual sort/search logic
4. **Gained features** (export, total row) with minimal effort
5. **Maintained custom styling** (status badge)
6. **Type safety** improved with proper TypeScript types

### What Changed
- **Lines of code**: Similar count but much less complex logic
- **State management**: Simplified (removed 3 state variables)
- **Features**: Gained export and total row
- **Maintainability**: Much easier to update
- **Consistency**: Now matches other refactored tables

### Performance Comparison
- **Original**: Manual sort/filter on every render
- **Refactored**: Optimized with useMemo and efficient algorithms
- **Result**: Faster interactions, better performance

---

## Another Example: Financial Report with Hierarchy

### Original (Complex Custom Table)

```typescript
// Complex custom implementation with 200+ lines
// - Manual hierarchy management
// - Custom expand/collapse logic
// - Manual total calculations
// - Complex state management
```

### After Refactoring

```typescript
import { UnifiedTable, TABLE_PRESETS } from '@/components/tables/UnifiedTable';

const FinancialReport = () => {
  const { data: backendData } = useFinancialData();

  const tableData = useMemo(() => ({
    sections: [
      {
        id: 'revenue',
        name: 'Revenue',
        summary: { actual: 1000000, budget: 950000 },
        level: 0,
        expandable: true,
        items: [
          { id: 'rev-1', product: 'Product A', actual: 600000, budget: 500000 },
          { id: 'rev-2', product: 'Product B', actual: 400000, budget: 450000 }
        ]
      },
      {
        id: 'expenses',
        name: 'Expenses',
        summary: { actual: 750000, budget: 800000 },
        level: 0,
        expandable: true,
        items: [
          { id: 'exp-1', category: 'Salaries', actual: 500000, budget: 520000 },
          { id: 'exp-2', category: 'Marketing', actual: 250000, budget: 280000 }
        ]
      }
    ]
  }), [backendData]);

  const columns = useMemo(() => [
    { key: 'name', header: 'Category', sticky: true },
    { key: 'actual', header: 'Actual', formatType: 'currency', align: 'right' },
    { key: 'budget', header: 'Budget', formatType: 'currency', align: 'right' }
  ], []);

  return (
    <UnifiedTable
      data={tableData}
      columns={columns}
      features={{
        ...TABLE_PRESETS.FINANCIAL,
        export: true
      }}
      title="Financial Report"
      totalRowConfig={{
        position: 'bottom',
        calculate: true,
        label: 'Net Income'
      }}
    />
  );
};
```

**Result:**
- **Code reduction**: 200+ lines → ~60 lines (70% reduction!)
- **Complexity reduction**: Massive simplification
- **Features gained**: Export, better formatting, consistent UX
- **Maintainability**: Much easier to update

---

## Tips for Using the Skill

1. **Have your table component ready** - Know which component you want to refactor
2. **Understand the data flow** - Know where data comes from
3. **Identify custom features** - Be ready to describe any unique functionality
4. **Test thoroughly** - Use the provided checklists
5. **Iterate if needed** - The skill can help adjust if something doesn't work perfectly
6. **Ask questions** - The skill is interactive and can clarify anything

## Common Questions During Refactoring

**Q: "My backend returns different field names. What do I do?"**
A: The skill will create a data adapter function to map fields.

**Q: "I have custom row actions (edit, delete). How do I preserve them?"**
A: The skill will add an actions column with custom rendering.

**Q: "My table has complex filtering with multiple dropdowns. Is that supported?"**
A: Yes, the skill will use customHeaderControls for custom filters.

**Q: "The data structure is very nested. Will this work?"**
A: Yes, UnifiedTable supports multi-level hierarchies. The skill will help structure it correctly.

**Q: "I need comments on my table. How do I add that?"**
A: The skill will use UnifiedTableWithCommentsWrapper and set up comment handlers.

---

*This example demonstrates the complete refactoring process from start to finish. Your actual refactoring may vary based on your specific table implementation.*
