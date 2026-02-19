# Table Refactoring Quick Reference

## Quick Start

1. **Invoke the skill**: Use `table-refactor` in Claude Code
2. **Specify your table**: Tell the skill which component to refactor
3. **Follow the phases**: The skill guides you through 6 phases
4. **Test thoroughly**: Verify all features work correctly
5. **Submit for review**: Use the provided checklist

## Data Structure Decision Tree

```
Is your data nested/hierarchical?
├─ NO → Use `{ data: [] }` with TABLE_PRESETS.BASIC
└─ YES → Use `{ sections: [] }` with appropriate preset
    ├─ Product catalog? → TABLE_PRESETS.CATALOG
    ├─ Corporate hierarchy? → TABLE_PRESETS.CORPORATE
    └─ Custom hierarchy? → TABLE_PRESETS.ACCORDION
```

## Feature Presets Cheat Sheet

| Preset | Use Case | Features Included |
|--------|----------|-------------------|
| `BASIC` | Simple tables | Sort, Search, Pagination |
| `ACCORDION` | Expandable rows | Sort, Search, Expand/Collapse |
| `COMMENTS` | Tables with comments | Sort, Search, Comments |
| `CATALOG` | Product catalogs | Hierarchy, Search, Pagination |
| `CORPORATE` | Org structures | Hierarchy, Expandable |
| `FINANCIAL` | Financial data | Sort, Totals, Export |

## Common Column Configurations

### Basic Text Column
```typescript
{ key: 'name', header: 'Name' }
```

### Sticky First Column
```typescript
{ key: 'name', header: 'Name', sticky: true }
```

### Currency Column
```typescript
{
  key: 'revenue',
  header: 'Revenue',
  formatType: 'currency',
  align: 'right',
  currencySymbol: '$',
  decimalPlaces: 2
}
```

### Percentage Column
```typescript
{
  key: 'growth',
  header: 'Growth %',
  formatType: 'percentage',
  align: 'right'
}
```

### Number Column
```typescript
{
  key: 'employees',
  header: 'Employees',
  formatType: 'number',
  align: 'right'
}
```

### Custom Renderer
```typescript
{
  key: 'status',
  header: 'Status',
  render: (value, row) => (
    <span className={`badge ${value === 'active' ? 'success' : 'warning'}`}>
      {value}
    </span>
  )
}
```

### Action Column
```typescript
{
  key: 'actions',
  header: 'Actions',
  render: (_, row) => (
    <div className="flex gap-2">
      <button onClick={() => handleEdit(row)}>Edit</button>
      <button onClick={() => handleDelete(row)}>Delete</button>
    </div>
  )
}
```

## Data Adapter Template

### Simple Data Adapter
```typescript
export const adaptMyTableData = (backendData: BackendType): TableData<FrontendType> => {
  return {
    data: backendData.items.map(item => ({
      id: item.itemId,
      name: item.displayName,
      email: item.emailAddress,
      // ... map other fields
    }))
  };
};
```

### Hierarchical Data Adapter
```typescript
export const adaptMyHierarchicalData = (backendData: BackendType): TableData<FrontendType> => {
  const mapChildren = (items: any[], level: number) => {
    return items.map(item => ({
      id: item.id,
      name: item.name,
      summary: { /* summary fields */ },
      level,
      expandable: item.hasChildren,
      children: item.children ? mapChildren(item.children, level + 1) : undefined,
      items: item.leafData || undefined
    }));
  };

  return {
    sections: mapChildren(backendData.categories, 0)
  };
};
```

## Component Templates

### Without Comments
```typescript
import { UnifiedTable, TABLE_PRESETS } from '@/components/tables/UnifiedTable';

const MyTable = () => {
  const { data: backendData, isLoading } = useMyData();

  const tableData = useMemo(() =>
    adaptMyTableData(backendData),
    [backendData]
  );

  const columns = useMemo(() => [
    { key: 'name', header: 'Name', sticky: true },
    { key: 'revenue', header: 'Revenue', formatType: 'currency', align: 'right' }
  ], []);

  if (isLoading) return <LoadingSpinner />;

  return (
    <UnifiedTable
      data={tableData}
      columns={columns}
      features={TABLE_PRESETS.BASIC}
      title="My Table"
      searchableColumns={['name']}
      pageSize={10}
    />
  );
};
```

### With Comments
```typescript
import { UnifiedTableWithCommentsWrapper } from '@/components/tables/UnifiedTable/UnifiedTableWithCommentsWrapper';
import { TABLE_PRESETS } from '@/components/tables/UnifiedTable';

const MyTableWithComments = () => {
  const { data: backendData, isLoading } = useMyData();

  const tableData = useMemo(() =>
    adaptMyTableData(backendData),
    [backendData]
  );

  const columns = useMemo(() => [
    { key: 'name', header: 'Name', sticky: true },
    { key: 'revenue', header: 'Revenue', formatType: 'currency', align: 'right' }
  ], []);

  if (isLoading) return <LoadingSpinner />;

  return (
    <UnifiedTableWithCommentsWrapper
      data={tableData}
      columns={columns}
      features={TABLE_PRESETS.COMMENTS}
      title="My Table with Comments"
      sectionType="my-table"
      commentsIdField="id"
      documentId="doc-123"
      onCommentCreate={handleCommentCreate}
      onCommentUpdate={handleCommentUpdate}
      onCommentDelete={handleCommentDelete}
      onCommentThreadDelete={handleCommentThreadDelete}
      searchableColumns={['name']}
      pageSize={10}
    />
  );
};
```

## Testing Checklist

### Functional Tests
- [ ] Data loads correctly
- [ ] All columns display properly
- [ ] Sorting works on all sortable columns
- [ ] Search/filtering works
- [ ] Pagination works (next, prev, page numbers)
- [ ] Expandable rows work (if hierarchical)
- [ ] Total rows calculate correctly (if enabled)
- [ ] Export functionality works (if enabled)
- [ ] Comments work (if enabled)
- [ ] Custom actions work

### Visual Tests
- [ ] Layout matches or improves original
- [ ] Styling is consistent with app theme
- [ ] Responsive on mobile devices
- [ ] Dark mode works (if applicable)
- [ ] Hover states work
- [ ] Focus states work (accessibility)

### Edge Cases
- [ ] Empty data (no rows)
- [ ] Single row
- [ ] Large dataset (100+ rows)
- [ ] Very long text in cells
- [ ] Null/undefined values
- [ ] Special characters in text

## Common Patterns

### Pattern 1: Backend Data Mismatch
**Solution**: Create adapter function
```typescript
const tableData = useMemo(() =>
  adaptBackendData(backendData),
  [backendData]
);
```

### Pattern 2: Custom Filtering
**Solution**: Use customHeaderControls
```typescript
<UnifiedTable
  data={filteredData}
  customHeaderControls={
    <select onChange={handleFilterChange}>
      <option>All</option>
      <option>Active</option>
    </select>
  }
/>
```

### Pattern 3: Server-Side Pagination
**Solution**: Handle in API service
```typescript
const { data, isLoading } = useQuery({
  queryKey: ['table-data', page, pageSize],
  queryFn: () => fetchData(page, pageSize)
});
```

### Pattern 4: Preserve Custom Actions
**Solution**: Add action column
```typescript
{
  key: 'actions',
  header: 'Actions',
  render: (_, row) => <ActionButtons row={row} />
}
```

## Troubleshooting

| Issue | Check | Solution |
|-------|-------|----------|
| Data not displaying | Data structure | Verify `{ data: [] }` or `{ sections: [] }` |
| Columns empty | Column keys | Ensure keys match data fields |
| Sorting not working | disableSorting | Set to `false` or omit |
| Comments not highlighting | commentsIdField | Verify ID field exists in all rows |
| Hierarchy not expanding | level/expandable | Ensure all sections have these props |
| Performance issues | Dataset size | Enable pagination |

## Backend Integration

### API Endpoint Template
```python
@router.get("/api/v2/my-table")
async def get_table_data(
    page: int = 1,
    page_size: int = 10,
    sort_by: Optional[str] = None,
    sort_direction: str = "asc",
    search: Optional[str] = None
):
    # Fetch data with parameters
    data = await fetch_original_data()

    # Transform to UnifiedTable format
    return {
        "data": [
            {
                "id": item.id,
                "name": item.display_name,
                # ... other fields
            }
            for item in data
        ]
    }
```

## Props Quick Reference

### Essential Props
```typescript
data: TableData<T>           // Required: { data: [] } or { sections: [] }
columns: ColumnDef<T>[]      // Required: Column definitions
features: TableFeatures      // Required: Feature configuration
```

### Common Optional Props
```typescript
title?: string
description?: string
searchableColumns?: string[]
pageSize?: number
initialSort?: SortConfig<T>
totalRowConfig?: TotalRowConfig<T>
customHeaderControls?: ReactNode
```

### Comments Props (UnifiedTableWithCommentsWrapper)
```typescript
sectionType: string          // Required for comments
commentsIdField: string      // Default: 'id'
documentId: string           // Required for comments
onCommentCreate: Function    // Required for comments
onCommentUpdate: Function    // Required for comments
onCommentDelete: Function    // Required for comments
```

## File Locations

- **Skill**: `.claude/skills/table-refactor/SKILL.md`
- **UnifiedTable**: `klair-client/src/components/tables/UnifiedTable/`
- **Usage Guide**: `klair-client/src/components/tables/UnifiedTable/USAGE.md`
- **Examples**: `klair-client/src/screens/components-demo/`
- **Types**: `klair-client/src/components/tables/UnifiedTable/types.ts`

## Best Practices

1. ✅ Always use `useMemo` for data transformations and column definitions
2. ✅ Create a separate adapter function for data transformation
3. ✅ Use TypeScript types for type safety
4. ✅ Test with empty data and edge cases
5. ✅ Keep existing functionality intact
6. ✅ Use proper presets as starting points
7. ✅ Document custom logic with comments
8. ✅ Handle loading and error states
9. ✅ Use pagination for large datasets
10. ✅ Follow project coding standards

## Resources

- **Full Documentation**: `klair-client/src/components/tables/UnifiedTable/USAGE.md`
- **Internal Details**: `klair-client/src/components/tables/UnifiedTable/INTERNAL.md`
- **Live Examples**: Visit `/components-demo` route in the application
- **Type Definitions**: `klair-client/src/components/tables/UnifiedTable/types.ts`

---

*Use this as a quick reference while the skill guides you through the refactoring process.*
