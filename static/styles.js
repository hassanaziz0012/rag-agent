const STYLES = {
    rewrittenQueryWrapper: "flex items-center gap-2 mb-2 ml-1",
    rewrittenQueryIcon: "w-4 h-4 text-gray-400 rotate-180", // Smaller icon size
    rewrittenQueryText: "text-xs font-medium text-gray-500 bg-white border border-gray-200 rounded-md px-2 py-1 shadow-sm", // Mini text box style
    
    searchCardsContainer: "flex gap-3 overflow-x-auto pb-4 scrollbar-thin",
    searchCard: "flex-shrink-0 w-72 p-5 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow", // More padding, white bg
    searchCardHeader: "flex justify-between items-start mb-3",
    searchCardSource: "text-xs font-medium text-gray-400 uppercase tracking-wide",
    searchCardScore: "text-xs font-bold text-[#d97757] bg-[#d97757]/10 px-2 py-1 rounded-full",
    searchCardText: "text-sm text-gray-600 leading-relaxed", // Full text display (removed line-clamp)

    aiBubble: "px-6 py-4 rounded-[20px] rounded-bl-[4px] bg-white text-gray-800 border border-gray-200 shadow-[0_2px_12px_rgba(0,0,0,0.06)] prose prose-sm prose-gray max-w-none",
    
    userBubble: "max-w-[80%] px-5 py-3 rounded-[18px] rounded-br-[4px] bg-gradient-to-br from-[#d97757] to-[#c4613f] text-white shadow-[0_4px_12px_rgba(217,119,87,0.3)]",
    
    responseWrapper: "max-w-[85%] flex flex-col gap-2",
    containerDiv: "flex justify-start mb-6"
};
