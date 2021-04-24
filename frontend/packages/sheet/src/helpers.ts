import {
  useLayoutEffect,
  useEffect,
  useState,
  useCallback,
  RefObject,
} from "react";

type ElementSize = {
  height: number;
  width: number;
};

// Should factor this into UI Components
function useElementSize(
  ref: RefObject<HTMLElement>,
  trackWindowResize: boolean = true
): ElementSize | null {
  const [size, setSize] = useState<ElementSize>(null);

  const sizeCallback = useCallback(() => {
    console.log(ref);
    if (ref.current == null) return;
    const { height, width } = ref.current.getBoundingClientRect();
    console.log("Size:", { height, width });
    setSize({ height, width });
  }, [ref]);

  useLayoutEffect(sizeCallback, [ref]);

  // Also respond on window resize (if "trackWindowResize" is set)
  useEffect(() => {
    if (!trackWindowResize) return;
    window.addEventListener("resize", sizeCallback);
    return function () {
      window.removeEventListener("resize", sizeCallback);
    };
  }, [sizeCallback]);

  return size;
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

export { useElementSize, useScrollOffset };
