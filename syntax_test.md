# Syntax Highlighting Test

This is a test of syntax highlighting for different programming languages.

## Python Code
```python
def fibonacci(n):
    """Generate fibonacci sequence up to n"""
    a, b = 0, 1
    result = []
    while a < n:
        result.append(a)
        a, b = b, a + b
    return result

# Example usage
numbers = fibonacci(100)
print(f"Fibonacci numbers less than 100: {numbers}")
```

## JavaScript Code
```javascript
const fibonacci = (n) => {
    // Generate fibonacci sequence up to n
    let result = [];
    let a = 0, b = 1;
    
    while (a < n) {
        result.push(a);
        [a, b] = [b, a + b];
    }
    
    return result;
};

// Example usage
const numbers = fibonacci(100);
console.log(`Fibonacci numbers less than 100: ${numbers}`);
```

## CSS Code
```css
.syntax-highlight {
    background-color: #272822;
    color: #f8f8f2;
    border-radius: 8px;
    padding: 15px;
    font-family: 'Courier New', monospace;
}

.syntax-highlight .keyword {
    color: #66d9ef;
    font-weight: bold;
}
```

## Bash/Shell Code
```bash
#!/bin/bash

# Function to generate fibonacci sequence
fibonacci() {
    local n=$1
    local a=0
    local b=1
    
    echo -n "Fibonacci numbers less than $n: "
    while [ $a -lt $n ]; do
        echo -n "$a "
        local temp=$((a + b))
        a=$b
        b=$temp
    done
    echo
}

# Example usage
fibonacci 100
```

## SQL Code
```sql
-- Create a table for fibonacci numbers
CREATE TABLE fibonacci_sequence (
    id INTEGER PRIMARY KEY,
    position INTEGER NOT NULL,
    value INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some fibonacci numbers
INSERT INTO fibonacci_sequence (position, value) VALUES
(0, 0),
(1, 1),
(2, 1),
(3, 2),
(4, 3),
(5, 5),
(6, 8),
(7, 13);

-- Query to get fibonacci numbers
SELECT position, value 
FROM fibonacci_sequence 
WHERE value < 100 
ORDER BY position;
```

This demonstrates syntax highlighting across multiple programming languages!
