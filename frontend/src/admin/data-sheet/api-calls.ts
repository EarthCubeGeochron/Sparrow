import { useAPIResult } from "@macrostrat/ui-components";
import { useState, useEffect } from "react";

const urlAPI = "http://localhost:5002/api/v2/models/sample";

export function MaterialCall() {
  const [materials, setMaterials] = useState([]);

  const init = useAPIResult(urlAPI, { has: "material" });

  useEffect(() => {
    if (init) {
      const materialslist = init.data.map((obj) => obj.material);
      const materials = materialslist.filter((str) => str.length < 15);

      const matSet = new Set(materials);
      const arrayMat = [...matSet];
      setMaterials(arrayMat);
    }
  }, [init]);
  return materials;
}

export function SampleNameCall() {
  const [names, setNames] = useState([]);

  const init = useAPIResult(urlAPI, { per_page: 3000 });

  useEffect(() => {
    if (init) {
      const names = init.data.map((obj) => obj.name);
      const nameList = [...new Set(names)];
      setNames(nameList);
    }
  }, [init]);
  return names;
}
