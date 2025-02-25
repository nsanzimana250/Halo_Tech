function exportToPDF() {
    const element = document.querySelector(".table-responsive");
    html2pdf().from(element).save("Companies.pdf");
}

function exportToExcel() {
    let table = document.querySelector("table");
    let html = table.outerHTML;
    let uri = "data:application/vnd.ms-excel," + encodeURIComponent(html);
    let link = document.createElement("a");
    link.href = uri;
    link.download = "Companies.xls";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function sharePDF() {
    const element = document.querySelector(".table-responsive");
    html2pdf().from(element).outputPdf('datauristring').then((pdfData) => {
        const link = document.createElement('a');
        link.href = pdfData;
        link.download = 'Companies.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        const pdfBlob = dataURItoBlob(pdfData);
        const pdfFile = new File([pdfBlob], 'Companies.pdf', { type: 'application/pdf' });
        const pdfUrl = URL.createObjectURL(pdfFile);

        openShareDialog(pdfUrl);
    });
}

function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

function openShareDialog(pdfUrl) {
    const shareText = "Check out this report!";
    const shareUrl = encodeURIComponent(pdfUrl);
    const socialLinks = {
        whatsapp: `https://api.whatsapp.com/send?text=${shareText} ${shareUrl}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${shareUrl}`,
        twitter: `https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}`,
        instagram: `https://www.instagram.com/?url=${shareUrl}`,
    };

    const shareDialog = `
        <div style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #ffffff;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            width: 300px;
            text-align: center;
            font-family: Arial, sans-serif;
        ">
            <h5 style="
                margin: 0 0 16px;
                font-size: 18px;
                color: #333333;
            ">
                Share via:
            </h5>
            <a href="${socialLinks.whatsapp}" target="_blank" style="
                display: block;
                margin: 12px 0;
                padding: 10px;
                border-radius: 8px;
                background: #25D366;
                color: white;
                text-decoration: none;
                font-weight: bold;
                transition: background 0.3s ease;
            ">WhatsApp</a>
            <a href="${socialLinks.facebook}" target="_blank" style="
                display: block;
                margin: 12px 0;
                padding: 10px;
                border-radius: 8px;
                background: #1877F2;
                color: white;
                text-decoration: none;
                font-weight: bold;
                transition: background 0.3s ease;
            ">Facebook</a>
            <a href="${socialLinks.twitter}" target="_blank" style="
                display: block;
                margin: 12px 0;
                padding: 10px;
                border-radius: 8px;
                background: #1DA1F2;
                color: white;
                text-decoration: none;
                font-weight: bold;
                transition: background 0.3s ease;
            ">Twitter</a>
            <a href="${socialLinks.instagram}" target="_blank" style="
                display: block;
                margin: 12px 0;
                padding: 10px;
                border-radius: 8px;
                background: #E4405F;
                color: white;
                text-decoration: none;
                font-weight: bold;
                transition: background 0.3s ease;
            ">Instagram</a>
            <button onclick="closeShareDialog()" style="
                margin-top: 20px;
                padding: 10px 20px;
                background: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                transition: background 0.3s ease;
            ">Close</button>
        </div>
    `;

    const dialogContainer = document.createElement('div');
    dialogContainer.innerHTML = shareDialog;
    dialogContainer.style.position = 'fixed';
    dialogContainer.style.top = '0';
    dialogContainer.style.left = '0';
    dialogContainer.style.width = '100%';
    dialogContainer.style.height = '100%';
    dialogContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    dialogContainer.style.zIndex = '999';
    dialogContainer.id = 'shareDialog';
    document.body.appendChild(dialogContainer);
}

function closeShareDialog() {
    const dialog = document.getElementById('shareDialog');
    if (dialog) {
        dialog.remove();
    }
}

