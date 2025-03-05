### 如何使用這個common

- 直接使用

```
cd /your/project/folder/
git clone https://github.com/YunTechAi-FreeSpaceTechnic/common.git
```

- 作為子模𧇿使用

```
cd /your/project/folder/
git submodule add https://github.com/YunTechAi-FreeSpaceTechnic/common.git common
```

[建立模型時的範例和說明 /example/build_model.py](https://github.com/YunTechAi-FreeSpaceTechnic/common/blob/main/example/build_model.py)  
[呼叫模型時的範例和說明 /example/invoke_model.py](https://github.com/YunTechAi-FreeSpaceTechnic/common/blob/main/example/invoke_model.py)

## Template

[repository](https://github.com/YunTechAi-FreeSpaceTechnic/model-template)

## Protocol Format

```mermaid
graph TD;
    A["Package (Variable Length)"] -->|1 byte| B[Package ID]
    B -->|決定 Data 格式| C[Data]

    subgraph Data 結構
        B1["Int32 (4 bytes)"]
        B2["Float32 (4 bytes)"]

        subgraph List 結構
            L1["List 長度 (Int32, 4 bytes)"]
            L2["元素1 (可能是 Int/Float/String/List)"]
            L3["元素2 (可能是 Int/Float/String/List)"]
            L4["元素N (可能是 Int/Float/String/List)"]
        end

        subgraph String 結構
            S1["String 長度 (Int32, 4 bytes)"]
            S2["字串內容 (UTF-8)"]
        end
    end

    C -->|可能是 Int32| B1
    C -->|可能是 Float32| B2
    C -->|可能是 List| L1
    L1 --> L2
    L2 -->|可能是 Int32| B1
    L2 -->|可能是 Float32| B2
    L2 -->|可能是 String| S1
    L2 -->|可能是 List| L1
    L3 -->|...| L4

    C -->|可能是 String| S1
    S1 --> S2

```

### 🎯 **完整封包結構**

1. **Package ID (1 byte)**

   - 決定 Data 格式

2. **Data（根據 ID 決定格式）**：
   - **Int32 (4 bytes)**
   - **Float32 (4 bytes)**
   - **List**：
     - `Int32 (4 bytes)` → **List 長度**
     - 多個 `data`（可以是 Int、Float、String 或 List）
   - **String**：
     - `Int32 (4 bytes)` → **字串長度**
     - `UTF-8 編碼字串`
