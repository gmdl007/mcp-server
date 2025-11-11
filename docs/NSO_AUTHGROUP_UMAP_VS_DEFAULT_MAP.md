# NSO Authgroup: umap vs default-map

Understanding the difference between `umap` and `default-map` in NSO authgroups.

---

## Quick Summary

- **`default-map`**: Default credentials used when **no umap matches** the NSO username
- **`umap`**: User-specific mappings that map **NSO usernames** to device credentials

---

## How NSO Selects Authentication Credentials

When NSO connects to a device, it follows this logic:

1. **Check if there's a `umap` entry matching the NSO username**
   - If found → Use those credentials
   - If not found → Continue to step 2

2. **Use `default-map` credentials**
   - This is the fallback when no umap matches

---

## Example 1: Using default-map Only

```bash
devices authgroups group netsim
  default-map remote-name admin
  default-map remote-password admin
```

**Behavior:**
- **Any NSO user** (admin, cisco, netsim, etc.) connecting to devices using this authgroup
- Will use: `admin/admin` credentials
- Because there are no umap entries, default-map is always used

**Use Case:** Simple setup where all NSO users use the same device credentials (like netsim devices)

---

## Example 2: Using umap Only (No default-map)

```bash
devices authgroups group cisco
  umap cisco
    remote-name cisco
    remote-password <encrypted>
  umap admin
    remote-name admin
    remote-password <encrypted>
```

**Behavior:**
- **NSO user "cisco"** → Uses `cisco/<password>` on device
- **NSO user "admin"** → Uses `admin/<password>` on device
- **NSO user "netsim"** → **ERROR!** No umap for "netsim" and no default-map

**Use Case:** Different NSO users need different device credentials

---

## Example 3: Using Both umap and default-map

```bash
devices authgroups group mixed
  default-map remote-name admin
  default-map remote-password admin
  umap cisco
    remote-name cisco
    remote-password <encrypted>
  umap operator
    remote-name readonly
    remote-password <encrypted>
```

**Behavior:**
- **NSO user "cisco"** → Uses `cisco/<password>` (matches umap)
- **NSO user "operator"** → Uses `readonly/<password>` (matches umap)
- **NSO user "admin"** → Uses `admin/admin` (no umap match, uses default-map)
- **NSO user "netsim"** → Uses `admin/admin` (no umap match, uses default-map)

**Use Case:** Most flexible - specific users get specific credentials, others get default

---

## Real-World Example: Your Setup

### Authgroup "cisco" (for dcloud routers)
```bash
devices authgroups group cisco
  umap cisco
    remote-name cisco
    remote-password <encrypted>
```

- **NSO user "cisco"** → Uses `cisco/<password>` on dcloud routers
- **NSO user "admin"** → **ERROR!** No default-map, no umap for "admin"

### Authgroup "netsim" (for netsim devices)
```bash
devices authgroups group netsim
  default-map remote-name admin
  default-map remote-password admin
```

- **Any NSO user** → Uses `admin/admin` on netsim devices
- Works for all users because default-map is always available

---

## Key Differences Table

| Feature | `default-map` | `umap` |
|---------|---------------|--------|
| **Purpose** | Default fallback credentials | User-specific credentials |
| **When Used** | When no umap matches NSO username | When umap key matches NSO username |
| **Required?** | No, but recommended | No |
| **Multiple Entries?** | Only one (it's a single container) | Yes, multiple umap entries allowed |
| **Key/Name** | No key (it's the default) | Key is the NSO username to match |

---

## Common Mistakes

### ❌ Mistake 1: Using `umap default` instead of `default-map`
```bash
# WRONG - This creates a umap entry with key "default"
devices authgroups group netsim
  umap default
    remote-name admin
    remote-password admin
```

**Problem:** NSO will only use this if the NSO username is literally "default". Other users won't match.

### ✅ Correct: Use `default-map`
```bash
# CORRECT - This is the actual default
devices authgroups group netsim
  default-map remote-name admin
  default-map remote-password admin
```

---

### ❌ Mistake 2: No default-map, and umap doesn't match
```bash
devices authgroups group mygroup
  umap cisco
    remote-name cisco
    remote-password <encrypted>
```

**Problem:** If NSO user "admin" tries to connect, there's no umap for "admin" and no default-map → **ERROR!**

### ✅ Solution: Add default-map
```bash
devices authgroups group mygroup
  default-map remote-name admin
  default-map remote-password admin
  umap cisco
    remote-name cisco
    remote-password <encrypted>
```

---

## Best Practices

1. **Always include `default-map`** - Provides fallback for any NSO user
2. **Use `umap` for specific users** - When different NSO users need different device credentials
3. **Use `default-map` only** - When all NSO users should use the same device credentials (simplest)

---

## Summary

- **`default-map`** = "What credentials to use when nothing else matches"
- **`umap`** = "What credentials to use for specific NSO users"

Think of it like this:
- `umap` = VIP list (specific users get specific treatment)
- `default-map` = General admission (everyone else gets this)

