import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Clock, User, Tag } from "lucide-react"

export default function TicketStatusCard() {
  const getProgressValue = (status) => {
    const progress = {
      'open': 25,
      'In Progress': 50,
      'resolved': 75,
      'closed': 100
    }
    return progress[status] || 0
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="text-lg font-medium">
            {props.title || 'Untitled Ticket'}
          </CardTitle>
          <Badge 
            variant="outline" 
          >
            {props.status || 'Unknown'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Progress value={getProgressValue(props.status)} className="h-2" />
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 opacity-70" />
              <span>{props.assignee || 'Unassigned'}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 opacity-70" />
              <span>{props.deadline || 'No deadline'}</span>
            </div>
            <div className="flex items-center gap-2 col-span-2">
              <Tag className="h-4 w-4 opacity-70" />
              <span>{props.tags?.join(', ') || 'No tags'}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}