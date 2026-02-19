# Table Refactor Skill

## Overview

This agent skill guides developers through refactoring existing custom table components to use the unified `UnifiedTable` and `UnifiedTableWithCommentsWrapper` components in the Klair project.

## Purpose

The Klair client application has many custom-built table components that were created separately without centralization. The `UnifiedTable` component was created to:
- Centralize table logic and features
- Provide consistent user experience across all tables
- Improve maintainability and reduce code duplication
- Offer advanced features like comments, hierarchical data, exports, etc.

This skill automates the refactoring process, making it easier for developers to migrate their custom tables to the unified component.

## How to Use

### Invoking the Skill

In Claude Code, simply invoke the skill:

```
table-refactor
```

Or use the Skill tool to activate it.

### What the Skill Does

The skill will guide you through a 6-phase process:

1. **Analysis Phase**: Examines your existing table implementation
   - Identifies data sources and structure
   - Maps columns and features
   - Analyzes current functionality

2. **Planning Phase**: Determines the best approach
   - Selects appropriate data structure (simple vs hierarchical)
   - Chooses the right feature preset
   - Plans data adapter layer if needed
   - Maps column definitions

3. **Implementation Phase**: Refactors the component
   - Creates data adapter functions
   - Defines column configurations
   - Replaces old table with UnifiedTable
   - Handles custom features

4. **Backend Integration Phase**: Ensures API compatibility
   - Reviews backend requirements
   - Creates backend adapters if needed
   - Updates API service calls

5. **Testing Phase**: Validates the implementation
   - Functional testing of all features
   - Visual comparison with original
   - Performance testing
   - Edge case testing

6. **Cleanup Phase**: Finalizes the refactoring
   - Removes old code
   - Updates documentation
   - Prepares for code review

## Prerequisites

Before using this skill:
- Have a specific table component you want to refactor
- Know where the component is located in the codebase
- Understand the current functionality of the table
- Have access to the backend API code (if changes are needed)

## What You'll Get

After running this skill:
- ✅ Refactored table component using UnifiedTable
- ✅ Data adapter functions (if needed)
- ✅ Backend adapter endpoints (if needed)
- ✅ Comprehensive testing checklist
- ✅ Updated documentation
- ✅ Code review checklist

## Key Features Supported

The UnifiedTable component supports:
- **Simple Data**: Flat array of objects
- **Hierarchical Data**: Multi-level nested structures
- **Sorting**: Column-based sorting
- **Search/Filtering**: Text-based search across columns
- **Pagination**: Client-side and server-side
- **Total Rows**: Calculated or custom totals
- **Export**: CSV and Excel exports
- **Comments**: Cell-level commenting with threads
- **Expandable Rows**: Accordion-style rows
- **Custom Renderers**: Custom cell and row rendering
- **Sticky Columns**: Fixed first column
- **Responsive Design**: Mobile-friendly layouts
- **Dark Mode**: Full dark mode support

## Reference Documentation

For detailed API documentation and examples, see:
- `klair-client/src/components/tables/UnifiedTable/USAGE.md` - Complete usage guide
- `klair-client/src/components/tables/UnifiedTable/INTERNAL.md` - Internal implementation details
- `/components-demo` - Live examples and demos

## Examples

### Example 1: Simple Table Refactoring

**Before:**
```typescript
const MyTable = () => {
  const [data, setData] = useState([]);

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
        </tr>
      </thead>
      <tbody>
        {data.map(row => (
          <tr key={row.id}>
            <td>{row.name}</td>
            <td>{row.email}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

**After:**
```typescript
import { UnifiedTable, TABLE_PRESETS } from '@/components/tables/UnifiedTable';

const MyTable = () => {
  const [data, setData] = useState([]);

  const columns = [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' }
  ];

  return (
    <UnifiedTable
      data={{ data }}
      columns={columns}
      features={TABLE_PRESETS.BASIC}
      title="My Table"
    />
  );
};
```

### Example 2: Table with Comments

**After Refactoring:**
```typescript
import { UnifiedTableWithCommentsWrapper } from '@/components/tables/UnifiedTable/UnifiedTableWithCommentsWrapper';
import { TABLE_PRESETS } from '@/components/tables/UnifiedTable';

const MyTableWithComments = () => {
  const [data, setData] = useState([]);

  const columns = [
    { key: 'name', header: 'Name', sticky: true },
    { key: 'revenue', header: 'Revenue', formatType: 'currency', align: 'right' }
  ];

  return (
    <UnifiedTableWithCommentsWrapper
      data={{ data }}
      columns={columns}
      features={TABLE_PRESETS.COMMENTS}
      title="My Table with Comments"
      sectionType="my-table"
      commentsIdField="id"
      documentId="doc-123"
      onCommentCreate={handleCommentCreate}
      onCommentUpdate={handleCommentUpdate}
      onCommentDelete={handleCommentDelete}
    />
  );
};
```

## Troubleshooting

### Skill Not Appearing

If the skill doesn't appear in your Claude Code:
1. Ensure the skill file is in `.claude/skills/table-refactor/SKILL.md`
2. Restart Claude Code
3. Check the YAML frontmatter is correctly formatted

### Skill Execution Issues

If the skill encounters issues:
1. Ensure you have read the UnifiedTable USAGE.md file
2. Check that your table component file exists and is accessible
3. Verify you have the necessary permissions to read/write files

### Need Help?

Consult the following resources:
- UnifiedTable USAGE.md documentation
- Ask the skill for clarification at any step
- Review the troubleshooting section in the skill file

## Contributing

To improve this skill:
1. Test it with different table refactoring scenarios
2. Document any issues or edge cases
3. Submit improvements to the skill file
4. Update this README with new examples

## Version History

- **v1.0.0** (2025-10-29): Initial release
  - Complete 6-phase refactoring process
  - Support for simple and hierarchical tables
  - Backend integration guidance
  - Comprehensive testing and cleanup

## License

This skill is part of the Klair project and follows the project's license.
