# Analysis Criteria

Use these criteria to systematically evaluate each implementation. Apply consistently to both branches for fair comparison.

## 1. Spec Compliance

**What to Check**:
- Are all required features implemented?
- Do features work as specified?
- Are acceptance criteria met?
- Are technical constraints respected?
- Are edge cases handled per spec?

**How to Evaluate**:
- Cross-reference spec requirements with implementation
- Check for missing features or functionality
- Verify behavior matches specified behavior
- Look for deviations or creative interpretations
- Note any features implemented beyond spec

**Documentation Notes**:
- List each spec requirement and its implementation status
- Identify gaps or incomplete implementations
- Flag any concerning deviations from spec
- Note positive additions or improvements

## 2. Code Quality

**What to Check**:
- Code organization and structure
- Readability and maintainability
- Design patterns and architectural choices
- Error handling and edge cases
- Code reusability and DRY principles
- Type safety (TypeScript/Python typing)
- Documentation and comments

**How to Evaluate**:
- Review file structure and module organization
- Assess naming conventions and code clarity
- Check for appropriate abstractions
- Look for code smells or anti-patterns
- Evaluate error handling robustness
- Check for proper type annotations
- Review inline documentation quality

**Documentation Notes**:
- Describe overall architecture and patterns used
- Highlight well-structured or problematic areas
- Note any technical debt or quick fixes
- Identify reusable components or utilities
- Comment on code readability and maintainability

## 3. Testing Coverage

**What to Check**:
- Unit test coverage and quality
- Integration test presence
- Test organization and structure
- Edge case and error condition testing
- Test maintainability
- Mock/stub usage appropriateness

**How to Evaluate**:
- Locate test files (*.test.ts, *.spec.ts, test_*.py, *_test.py)
- Review test coverage of key functionality
- Check for testing of edge cases and errors
- Assess test quality (not just quantity)
- Look for flaky or unreliable tests
- Evaluate test documentation

**Documentation Notes**:
- Summarize testing approach (unit, integration, e2e)
- List coverage of major features
- Identify untested or poorly tested areas
- Note test quality and maintainability
- Flag any testing concerns or gaps

## 4. Performance Considerations

**What to Check**:
- Algorithm efficiency (time/space complexity)
- Database query optimization
- Caching strategies
- Unnecessary re-renders (React) or computations
- Bundle size impact (frontend)
- API response times and efficiency
- Memory usage patterns

**How to Evaluate**:
- Review critical path code for efficiency
- Check for N+1 queries or inefficient operations
- Look for memoization/caching where appropriate
- Identify potential bottlenecks
- Review data structure choices
- Check for unnecessary work or redundant operations

**Documentation Notes**:
- Describe performance-critical sections
- Note optimization strategies employed
- Identify potential performance issues
- Compare algorithm choices and their complexity
- Flag any serious performance concerns

## General Analysis Tips

1. **Be Systematic**: Apply each criterion consistently to both implementations
2. **Be Specific**: Reference actual code with file:line format
3. **Be Objective**: Focus on measurable qualities, not preferences
4. **Be Fair**: Consider context and constraints each implementation faced
5. **Be Thorough**: Don't skip criteria even if one implementation seems clearly better

## Output Structure

For each criterion, document:
- **Summary**: High-level assessment (1-2 sentences)
- **Details**: Specific findings with code references
- **Rating**: Excellent / Good / Fair / Poor
- **Key Concerns**: Any critical issues (if applicable)
