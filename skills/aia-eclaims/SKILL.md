# AIA eClaims Automation Skill

## Trigger
Use this skill whenever the user wants to submit an AIA eClaims form for a client.
Form URL: https://www.aia.com.hk/zh-hk/customer-corner/ichange/e-claim/individual-claim-form.html

## Architecture
- 7-step AEM Adaptive Form in a same-origin iframe (window.frames[0].document accessible)
- Portal: https://aiahk-blob01-prd.aia.com.hk/agency/zh-hk/home
- Iframe src contains: individual-claim.html

## Key JS Patterns

### Set visible dropdowns (select.dropdown class)
const iframeDoc = window.frames[0].document;
const visibleSelects = Array.from(iframeDoc.querySelectorAll('select.dropdown')).filter(s => s.getBoundingClientRect().width > 0);
// Index 0=insured, 1=accident yes/no (acc/med), 2=related to previous (Y/N)

### Click Next/Back buttons
Array.from(iframeDoc.querySelectorAll('button')).find(b => b.textContent.includes('下一步')).click();

### Referral letter - previously submitted
Array.from(iframeDoc.querySelectorAll('label,span')).find(l => l.textContent.trim() === '客戶之前已遞交轉介信').click();

### Provider search
// SAMPLE PHYSIO CLINIC LIMITED = MP00000
// Set value on select (index 2 of visible selects on upload page)

## File Upload Workaround
file_upload tool returns Not Allowed for iframe inputs. Use CORS server:
1. Run: nohup python3 /tmp/cors_server.py > /tmp/corsserver.log 2>&1 &
2. cors_server.py serves /tmp with Access-Control-Allow-Origin: *
3. In browser JS: fetch blob, use iframe File/DataTransfer constructors, Object.defineProperty on input.files

BETTER: Use Playwright setInputFiles() - works natively on iframe inputs.

## Remove Button Warning
- .s5.removeBtn (H5) = remove individual FILE (safe)
- .lk2.removeBtn (A) = remove entire RECEIPT SECTION (dangerous)

## Typical Client: CHAN TAI MAN, Policy B000000001
- Accident: 01/01/2025, sports, neck/shoulder/chest, Hong Kong
- Physio provider: SAMPLE PHYSIO CLINIC LIMITED (MP00000)
- Treatment type value: 4 (物理治療)
- Currency: 048 (港元)
- Referral: previously submitted
