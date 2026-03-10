"use client";

import { useEffect, useState } from "react";

export function ResizeHandle({
  onResize
}: {
  onResize: (delta: number) => void;
}) {
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    if (!dragging) {
      return;
    }

    const onMouseMove = (event: MouseEvent) => {
      onResize(event.movementX);
    };
    const onMouseUp = () => {
      setDragging(false);
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [dragging, onResize]);

  return (
    <div
      aria-hidden
      className="group flex w-3 cursor-col-resize items-center justify-center"
      onMouseDown={() => setDragging(true)}
    >
      <div className="h-20 w-[2px] rounded-full bg-[rgba(13,37,48,0.14)] transition group-hover:h-28 group-hover:bg-[rgba(15,139,141,0.45)]" />
    </div>
  );
}
