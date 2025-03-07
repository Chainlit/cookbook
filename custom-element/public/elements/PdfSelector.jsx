import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircle, Circle, FileText } from "lucide-react";
import { useState } from "react";

export default function PdfSelector() {
    const { files, selected_files = [] } = props; // Ensure selected_files exists
    const [selected, setSelected] = useState(null);

    const handleSelect = (file) => {
        setSelected(file);

        // Toggle selection
        const updatedFiles = selected_files.includes(file)
            ? selected_files.filter((f) => f !== file) // Remove if already selected
            : [...selected_files, file]; // Add if not selected

        // Update the element's props in Chainlit
        updateElement({ ...props, selected_files: updatedFiles });

        // Call Python action in Chainlit
        console.log("Calling action: handle_file_selection with", updatedFiles);
        callAction(
            {
                name: "handle_file_selection",
                payload: { selected_files: updatedFiles }
            }
        );
    };

    return (
        <div className="space-y-2">
            {files.map((file, index) => (
                <Card key={index} className="flex items-center justify-between p-3">
                    <div className="flex items-center space-x-2">
                        <FileText className="text-gray-500" />
                        <span className="text-sm font-medium">{file}</span>
                    </div>
                    <Button
                        variant={selected_files.includes(file) ? "default" : "outline"}
                        onClick={() => handleSelect(file)}
                    >
                        {selected_files.includes(file) ? <CheckCircle className="mr-1" /> :
                            <Circle className="text-gray-400" />
                        }
                    </Button>
                </Card>
            ))}
        </div>
    );
}
