/* VisionBoard AI — Bounding Box Overlay Canvas Renderer */

function renderBoundingBoxes(canvasId, imageId, objectsData) {
  const canvas = document.getElementById(canvasId);
  const imgElem = document.getElementById(imageId);

  if (!canvas || !imgElem || !objectsData) return;

  const ctx = canvas.getContext('2d');

  function resizeAndDraw(highlightIndex = -1) {
    const width = imgElem.clientWidth;
    const height = imgElem.clientHeight;

    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);

    objectsData.forEach((obj, idx) => {
      const box = obj.box;
      const x = box.x * width;
      const y = box.y * height;
      const w = box.width * width;
      const h = box.height * height;

      const isHighlighted = (idx === highlightIndex);

      // Color styling based on object class or highlight
      ctx.lineWidth = isHighlighted ? 4 : 2;
      ctx.strokeStyle = isHighlighted ? '#00F2FE' : 'rgba(79, 172, 254, 0.8)';
      ctx.fillStyle = isHighlighted ? 'rgba(0, 242, 254, 0.25)' : 'rgba(0, 242, 254, 0.1)';

      // Draw Rectangle
      ctx.beginPath();
      ctx.rect(x, y, w, h);
      ctx.fill();
      ctx.stroke();

      // Draw Label Badge
      const labelText = `${obj.object_name} ${(obj.confidence * 100).toFixed(0)}%`;
      ctx.font = '600 12px "Outfit", sans-serif';
      const textWidth = ctx.measureText(labelText).width;

      ctx.fillStyle = isHighlighted ? '#00F2FE' : '#0F172A';
      ctx.fillRect(x, y > 24 ? y - 24 : y, textWidth + 12, 22);

      ctx.fillStyle = isHighlighted ? '#000000' : '#FFFFFF';
      ctx.fillText(labelText, x + 6, y > 24 ? y - 9 : y + 15);
    });
  }

  // Draw once image loads
  if (imgElem.complete) {
    resizeAndDraw();
  } else {
    imgElem.onload = () => resizeAndDraw();
  }

  window.addEventListener('resize', () => resizeAndDraw());

  // Attach hover events to object tags
  document.querySelectorAll('.object-tag-badge').forEach((badge) => {
    badge.addEventListener('mouseenter', () => {
      const idx = parseInt(badge.getAttribute('data-object-index'), 10);
      resizeAndDraw(idx);
    });
    badge.addEventListener('mouseleave', () => {
      resizeAndDraw(-1);
    });
  });
}
