import * as React from "react";
import { createRoot } from "react-dom/client";
import { Button } from "reactstrap";

const root = createRoot(document.body);
root.render(<Button color="danger">Test!</Button>);
