import { useLayoutEffect, useEffect, useState, useCallback } from "react";

// Should factor this into UI Components
function useElementHeight(ref: React.RefObject<HTMLElement>): number | null {
  const [height, setHeight] = useState<number>(null);

  const setSize = useCallback(() => {
    if (ref.current == null) return;
    const { height } = ref.current.getBoundingClientRect();
    setHeight(height);
  }, [ref.current]);

  useLayoutEffect(setSize, [ref.current]);

  // Also respond on window resize
  useEffect(() => {
    window.addEventListener("resize", setSize);
    return function() {
      window.removeEventListener("resize", setSize);
    };
  }, [ref.current]);

  return height;
}

function useScrollOffset(ref: React.RefObject<HTMLElement>): number {
  const [offset, setOffset] = useState(0);
  useEffect(() => {
    ref.current?.addEventListener("scroll", (evt) => {
      const el = <HTMLElement>evt.target;
      setOffset(el.scrollTop);
    });
  }, [ref.current]);
  return offset;
}

export { useScrollOffset, useElementHeight };
