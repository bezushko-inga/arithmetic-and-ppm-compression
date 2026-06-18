# Arithmetic and PPM Compression

Python implementation of two lossless data compression algorithms:
- Adaptive Arithmetic Coding
- PPM (Prediction by Partial Matching)

## Requirements
```bash
pip install -r requirements.txt
```
## Usage
### Arithmetic Coding
- Compress
```bash
python compress.py --input input.txt --output compressed.bin --mode c --method ari
```
- Decompress
```bash
python compress.py --input input.txt --output compressed.bin --mode d --method ari
```

### PPM
- Compress
```bash
python compress.py --input input.txt --output compressed.bin --mode c --method ppm
```
- Decompress
```bash
python compress.py --input input.txt --output compressed.bin --mode d --method ppm
```

## Project Structure

```text
.
├── compress.py              
├── ari.py                   
├── ppm.py                  
├── requirements.txt     
├── testing/
│   ├── __init__.py          
│   ├── command.py         
│   └── compressor.py     
└── tests/
    ├── test_1              
    ├── test_2               
    ├── test_3          
    ├── test_4     
    ├── test_5          
    ├── test_6           
    └── test_7            
```

## Benchmark Results

The compressors were evaluated on public and private benchmark test files. The tables show compressed file sizes in bytes and compression ratios.

## ARI Results

<table>
<tr>
<th rowspan="2">Method</th>
<th colspan="9">Public Tests</th>
<th colspan="6">Private Tests</th>
</tr>

<tr>
<th>test_1</th>
<th>test_2</th>
<th>test_3</th>
<th>test_4</th>
<th>test_5</th>
<th>test_6</th>
<th>test_7</th>
<th>Total Size</th>
<th>Ratio</th>

<th>test_8</th>
<th>test_9</th>
<th>test_10</th>
<th>test_11</th>
<th>Total Size</th>
<th>Ratio</th>
</tr>

<tr>
<td>Original</td>
<td>13</td>
<td>13095</td>
<td>226304</td>
<td>0</td>
<td>1000000</td>
<td>1000000</td>
<td>1000000</td>
<td>3239412</td>
<td>1.000</td>

<td>2152069</td>
<td>3725728</td>
<td>3102943</td>
<td>1822720</td>
<td>10803460</td>
<td>1.000</td>
</tr>

<tr>
<td>ARI</td>
<td>18</td>
<td>7969</td>
<td>170470</td>
<td>4</td>
<td>439086</td>
<td>4015</td>
<td>140850</td>
<td>762412</td>
<td>0.235</td>

<td>1095573</td>
<td>2537750</td>
<td>2005697</td>
<td>1223468</td>
<td>6862488</td>
<td>0.635</td>
</tr>

<tr>
<td>Huffman Baseline</td>
<td>50</td>
<td>8170</td>
<td>194661</td>
<td>8</td>
<td>443223</td>
<td>10</td>
<td>500056</td>
<td>1146178</td>
<td>0.354</td>

<td>1087219</td>
<td>3057461</td>
<td>2115415</td>
<td>1641935</td>
<td>7902030</td>
<td>0.731</td>
</tr>
</table>

## PPM Results

<table>
<tr>
<th rowspan="2">Method</th>
<th colspan="9">Public Tests</th>
<th colspan="6">Private Tests</th>
</tr>

<tr>
<th>test_1</th>
<th>test_2</th>
<th>test_3</th>
<th>test_4</th>
<th>test_5</th>
<th>test_6</th>
<th>test_7</th>
<th>Total Size</th>
<th>Ratio</th>

<th>test_8</th>
<th>test_9</th>
<th>test_10</th>
<th>test_11</th>
<th>Total Size</th>
<th>Ratio</th>
</tr>

<tr>
<td>Original</td>
<td>13</td>
<td>13095</td>
<td>226304</td>
<td>0</td>
<td>1000000</td>
<td>1000000</td>
<td>1000000</td>
<td>3239412</td>
<td>1.000</td>

<td>2152069</td>
<td>3725728</td>
<td>3102943</td>
<td>1822720</td>
<td>10803460</td>
<td>1.000</td>
</tr>

<tr>
<td>PPM</td>
<td>18</td>
<td>6671</td>
<td>158990</td>
<td>4</td>
<td>4030</td>
<td>4014</td>
<td>7477</td>
<td>181204</td>
<td>0.056</td>

<td>690164</td>
<td>1823630</td>
<td>1291600</td>
<td>906064</td>
<td>4711458</td>
<td>0.436</td>
</tr>

<tr>
<td>ZIP Default</td>
<td>175</td>
<td>6381</td>
<td>130155</td>
<td>162</td>
<td>2126</td>
<td>1148</td>
<td>7967</td>
<td>148114</td>
<td>0.046</td>

<td>585291</td>
<td>1337800</td>
<td>449744</td>
<td>670763</td>
<td>3043598</td>
<td>0.282</td>
</tr>

<tr>
<td>RAR Default</td>
<td>85</td>
<td>6414</td>
<td>113663</td>
<td>72</td>
<td>162</td>
<td>147</td>
<td>4019</td>
<td>124562</td>
<td>0.038</td>

<td>487253</td>
<td>1148917</td>
<td>348160</td>
<td>605321</td>
<td>2589651</td>
<td>0.240</td>
</tr>
</table>
