import {render,screen,fireEvent,cleanup} from '@testing-library/react'
import {afterEach,describe,it,expect,vi} from 'vitest'
import {MemoryRouter} from 'react-router-dom'
import {Status,PageHeader,ResourceTable} from '../../src/components/ui/Shared'
import {formatMoney,api} from '../../src/services/api'
afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals()})
describe('operational console',()=>{
 it('labels states without implying inference',()=>{render(<Status value="not_executed"/>);expect(screen.getByText('not executed')).toBeVisible()})
 it('provides an accessible heading',()=>{render(<PageHeader title="Invoices" description="Ledger balances"/>);expect(screen.getByRole('heading',{level:1})).toHaveTextContent('Invoices')})
 it('formats currency',()=>expect(formatMoney('1200.25','ZAR')).toContain('1'))
 it('shows API permission errors',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,headers:new Headers({'content-type':'application/json'}),json:async()=>({detail:'Role does not permit this action'})}));await expect(api('/invoices')).rejects.toThrow('Role does not permit this action')})
 it('renders loaded records and search',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,headers:new Headers({'content-type':'application/json'}),json:async()=>({items:[{id:'i',reference:'INV-001',status:'open'}],total:1})}));render(<MemoryRouter><ResourceTable resource="invoices" columns={[["reference","Invoice"],["status","Status"]]}/></MemoryRouter>);expect(await screen.findByText('INV-001')).toBeVisible();fireEvent.change(screen.getByLabelText('Search invoices'),{target:{value:'customer'}});expect(screen.getByLabelText('Search invoices')).toHaveValue('customer')})
})
