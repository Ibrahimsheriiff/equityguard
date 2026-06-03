export default function StockCard({ ticker, name, price, change, selected, onSelect }) {
    const pos = change >= 0
    return (
      <div
        onClick={onSelect}
        className={`bg-surface rounded-xl p-4 cursor-pointer transition-all border ${
          selected
            ? 'border-teal shadow-[0_0_0_1px_#00d4aa] bg-[#0a1e1a]'
            : 'border-border hover:border-teal/40'
        }`}
      >
        <div className="text-text font-bold text-sm">{ticker}</div>
        <div className="text-muted text-xs mt-0.5 mb-2">{name}</div>
        <div className="text-text font-bold text-lg">${price}</div>
        <div className={`text-sm font-medium ${pos ? 'text-teal' : 'text-red'}`}>
          {pos ? '+' : ''}{change}%
        </div>
      </div>
    )
  }