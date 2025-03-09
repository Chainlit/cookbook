import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, ChevronRight } from "lucide-react";

export default function FollowUpSuggestions() {
  const [selectedIndex, setSelectedIndex] = useState(null);
  
  // Default suggestions if none provided in props
  const suggestions = props.suggestions || [
    "Can you explain this in more detail?",
    "What are some examples of this?",
    "How would I implement this?"
  ];
  
  const handleSuggestionClick = (suggestion, index) => {
    setSelectedIndex(index);
    // Send the suggestion as a user message
    sendUserMessage(suggestion);
  };
  
  return (
    <Card className="w-full max-w-md border-2 border-primary/10">
      <CardHeader className="pb-2">
        <CardTitle className="text-md font-medium flex items-center gap-2">
          <MessageSquare className="h-4 w-4" />
          {props.title || "Follow-up Suggestions"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-2">
          {suggestions.map((suggestion, index) => (
            <Button
              key={index}
              variant={selectedIndex === index ? "default" : "outline"}
              className="justify-between text-left font-normal hover:bg-primary/10 transition-all"
              onClick={() => handleSuggestionClick(suggestion, index)}
              disabled={selectedIndex !== null}
            >
              <span>{suggestion}</span>
              <ChevronRight className="h-4 w-4 ml-2 opacity-70" />
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}