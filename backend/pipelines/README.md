# Sparrow pipelines

Data models and pipelines for bringing data into [Sparrow](https://sparrow-data.org).

A pipeline turns files into records and knows nothing about where they go, so it
can be written and rehearsed on a laptop with only this package installed. The
same pipeline object is what a Sparrow server runs as a task.

```python
from sparrow.pipelines import Analysis, Datum, DatumType, Pipeline, Sample, Session


class StableIsotopes(Pipeline):
    name = "stable-isotopes"
    pattern = "*.csv"

    def read(self, path):
        for row in read_rows(path):
            yield Session(
                date=row.date,
                technique="Stable isotope measurements",
                sample=Sample(name=row.sample),
                analysis=[
                    Analysis(
                        datum=[
                            Datum(
                                value=row.d13c,
                                error=row.d13c_error,
                                type=DatumType(parameter="delta13c", unit="permille"),
                            )
                        ]
                    )
                ],
            )
```

```sh
# Build and validate records; nothing is sent anywhere
sparrow run my_lab.pipelines:StableIsotopes ./data

# Send them to a lab (the token is read from SPARROW_API_TOKEN)
sparrow run my_lab.pipelines:StableIsotopes ./data --api https://sparrow.my-lab.org

# Once a lab's plugin has added the pipeline, load it in the lab's backend
sparrow run stable-isotopes

# The shape of a record
sparrow-pipeline schema session
```

`sparrow run` takes a task name or a pipeline. A name containing a colon is a
pipeline to run on this machine; it is handed to `sparrow-pipeline run`, which
this package installs and which works without the `sparrow` command too.

Records are plain [Pydantic](https://docs.pydantic.dev) models (`sparrow.pipelines.models`).
Vocabulary terms such as materials, techniques and units are strings; Sparrow
creates a term the first time it is used.

A sink is where records go. `DryRunSink` and `APISink` are here; a Sparrow
server adds one that writes to its database and tracks which files have been
loaded.
